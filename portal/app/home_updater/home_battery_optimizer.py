import requests
from django.conf import settings
import numpy as np
import json as json


def avg_power_for_device(parm_device_id):
    from app.models import HomeDeviceData

    try:
        recs = HomeDeviceData.objects.filter(home_device_id=parm_device_id)
        power_p_list = list()
        print ('No of records to be processed ' , recs.count())
        # Bypass process if no records for home
        if recs.count() > 0:
            for rec in recs:
                # parse required field from Json , if the fields are not present bypass record process next
                try :
                    val = json.loads(rec.device_data)['processed']['POWER-P']
                    #print (val)
                    power_p_list.append(val)
                except:
                    pass
            return np.average(np.asarray(power_p_list))
        else:
            return (0)

    except HomeDeviceData.DoesNotExist as e:
        print('Error retrieving home device data  for device id: ', parm_device_id)
        print(e)




def optimize_home_battery():
    # the device id is hard coded , introduce a loop if needed
    # Step 1 - get average home power f --> avg_power_for_device
    # Step 2 - Call optimization function f --> local_optimization_solve

    import  app.algorithms.local_controller as lcontrol

    # Get Average power consumption

    P_avg = avg_power_for_device(1) # device is hard coded , introduce dynamic calls if needed.


    print('Average Output is ', P_avg)
    print('Proceeding to optimization run ')

    # Example home with solar run
    lambda_b = 0.01
    lambda_cap = 100
    T = 24 * 4  # 15 minute resolution
    t_res = 15.0/60.0
    Qmin = 0
    Qmax = 12
    cmax = Qmax/3.0
    dmax = Qmax/3.0

    #used P_avg
    #P = np.array([3 * np.sin(x * 2 * np.pi / T - np.pi) + 2 for x in np.arange(T)])
    Q0 = Qmax / 2.0

    gamma_l = 0.9999
    gamma_d = 0.95
    gamma_c = 0.95
    lambda_e = np.hstack((.202 * np.ones((1, 16*4)), .463 * np.ones((1, 5*4)), .202 * np.ones((1, 3*4))))
    umin = -2*np.ones(T)
    umax = 6*np.ones(T)

    # Call optimizer
    c, d, Q, bounds_cost, status = lcontrol.local_optimization_solve(P_avg, lambda_b, lambda_cap, T, t_res, Qmin, Qmax, Q0,
                                                        cmax, dmax, gamma_l, gamma_d, gamma_c, lambda_e, umin, umax)

    print ('Output from the model , C -->' , c , 'D-->',d , 'Q-->', Q, 'bounds_cost-->',bounds_cost, 'status-->',status)


