var plotNoControl = plotNoControl || {},
    timeFrame,
    netPowerAllTransposed,
    qAllTransposed,
    solarAllTransposed,
    uAllTransposed,
    voltageAllTransposed;

// hard code the results of the algorithms
timeFrame = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48];

netPowerAllTransposed = [[20.0, 8.1606, 11.577, 3.636, 0.8094, 3.2478, 0.4674], [21.0, 11.324399999999999, 9.013200000000001, 3.6816, 3.5844, 3.591, 0.4674], [22.0, 10.95, 10.2744, 3.9492, 2.901, 3.6336, 0.4662], [25.0, 10.767599999999998, 12.708, 2.9868, 3.3876, 3.9036, 0.4896], [16.0, 8.2116, 7.965, 3.5724, 2.8038, 1.3368, 0.4986], [22.0, 10.6572, 11.047199999999998, 3.5976, 3.4524, 3.0708, 0.5364], [21.0, 11.102226010710751, 9.312992135802277, 4.043281405973368, 3.350601878533068, 3.1643424454669504, 0.544000280737365], [38.0, 28.403182554309595, 18.797801558851216, 8.199233268751483, 7.887611836718223, 7.415871379948379, 4.900466068891513], [36.0, 27.087131676380764, 18.538225565573896, 7.448522610714406, 7.333112664760175, 7.474688853381382, 4.830807547524798], [31.0, 25.25026918834523, 15.408339896514908, 7.712800302147639, 5.190845767773036, 7.728474467815371, 4.618148650609182], [27.0, 23.414038243751016, 13.972893148434919, 6.869544487132519, 6.088614018250391, 6.62223977692, 3.8336399614481067], [22.0, 19.41205817540908, 13.200150479697728, 6.7465332695166955, 3.4753556278649866, 5.810162012650552, 3.380007265376845], [26.0, 21.368215562055383, 14.505651519721734, 6.614268855065112, 4.538508118682166, 6.513288851609248, 3.702149736698857], [25.0, 21.588054331608905, 13.312739286752638, 6.343509828409909, 6.301679212163758, 5.695237156456532, 3.247628134578708], [29.0, 23.31024725845271, 15.251367108876234, 6.491529631354327, 7.1585278591594115, 6.078291860014523, 3.5818979079244473], [30.0, 22.59189846561645, 17.5417941045257, 6.079233139231737, 6.4014577276098885, 6.743428494874589, 3.3677791039002374], [-34.0, -31.04913731780065, -25.015543075844583, -6.262328725363668, -9.522853145984403, -5.990794235117254, -9.273161211335323], [-23.0, -21.526208879624825, -23.005742744559257, -5.32921788728604, -1.6785617321493453, -5.940379538793117, -8.578049721396322], [-19.0, -23.503351777930853, -16.07527442058347, -4.941546562006263, -5.32637584249707, -5.3238645298172536, -7.911564843610266], [-17.0, -24.888000000000005, -12.7146, -4.783800000000001, -7.048200000000001, -5.345400000000001, -7.710600000000001], [-20.0, -22.425600000000003, -18.354, -4.825800000000001, -4.764600000000001, -5.161200000000001, -7.674000000000001], [17.0, 10.835999999999999, 6.0485999999999995, 3.8496, 3.2448, 3.0126, 0.729], [23.0, 11.1504, 10.932, 3.6666, 3.4218, 3.3576, 0.7044], [22.0, 10.7358, 10.455599999999999, 3.7224, 3.5352, 2.7882, 0.69], [27.0, 11.798399999999999, 14.3052, 3.8262, 3.8982, 3.4236, 0.6504], [21.0, 11.306999999999999, 9.370800000000001, 3.6492, 3.267, 3.7014, 0.6894], [15.0, 8.731200000000001, 6.6426, 3.6768, 2.7252, 1.5894, 0.7398], [8.0, 3.7121999999999997, 4.3848, 1.4982, 0.4224, 1.0098, 0.7818], [13.0, 10.2912, 3.2346, 3.4746, 3.2202, 2.8338, 0.7626], [12.0, 8.3682, 3.4842, 2.0742, 2.9166, 2.61, 0.7674], [18.0, 12.964726371696628, 4.448886374826275, 3.61127122159319, 5.807270851163692, 2.802997637374421, 0.7431866615653243], [44.0, 29.877860549450872, 22.078402076260943, 7.96688762325103, 10.210715271036397, 6.682412762355833, 5.017844892807608], [42.0, 26.75678534327985, 23.412234148158454, 7.962494755358594, 7.0009422009710764, 6.78914434338633, 5.0042040435638535], [29.0, 24.985545494546752, 13.618994598756515, 7.509122740938067, 7.044564729781576, 5.951575866265177, 4.480282157561933], [28.0, 24.57315865603318, 13.074765895187216, 7.17381330788492, 7.903543945002065, 5.042382266452116, 4.4534191366940785], [25.0, 20.656918418416712, 14.298441998008306, 6.4500220558994545, 6.227012342408837, 4.062372101793512, 3.9175119183149105], [20.0, 19.135506671189894, 11.577201110897562, 5.988536109372579, 4.932872383989905, 4.862892578479984, 3.351205599347426], [21.0, 18.037295579926738, 13.528089245197544, 5.613880244592743, 4.279799840091639, 4.645475445660673, 3.498140049581683], [19.0, 17.046238424059464, 12.95656781117253, 3.2097470706956495, 5.199188860685979, 5.261543384450344, 3.375759108227492], [16.0, 14.892647905650806, 12.175436943710185, 3.504867935220962, 3.946578239833168, 3.836157080880473, 3.605044649716204], [-37.0, -33.40030313798468, -26.051121069236252, -9.143245619850974, -6.804560868469812, -8.736137511845936, -8.716359137817959], [-27.0, -28.05305437857014, -20.842815739503322, -5.312031328677483, -6.365656558918866, -8.18979090023142, -8.185575590742367], [-25.0, -26.470561869645145, -19.672904181881805, -4.6997620357459375, -8.097635722854163, -6.164729597863845, -7.508434513181202], [-21.0, -26.163, -15.858600000000001, -4.886400000000001, -7.8588000000000005, -6.063000000000001, -7.354800000000001], [-23.0, -25.697400000000002, -17.8782, -4.939800000000001, -5.959200000000001, -7.4076, -7.3908000000000005], [19.0, 8.547, 10.1382, 3.4698, 3.0504, 1.017, 1.0098], [21.0, 8.571, 11.6082, 3.7872, 1.2468, 2.5404, 0.9966], [12.0, 8.817, 2.976, 3.444, 3.483, 0.8598, 1.0302]]
qAllTransposed = [[0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [9.333333333333332, 3.111111111111111, 3.111111111111111, 3.111111111111111, 3.111111111111111], [13.999999999999998, 4.666666666666667, 4.666666666666667, 4.666666666666667, 4.666666666666667], [18.666666666666664, 6.222222222222222, 6.222222222222222, 6.222222222222222, 6.222222222222222], [23.33333333333333, 7.777777777777778, 7.777777777777778, 7.777777777777778, 7.777777777777778], [27.999999999999993, 9.333333333333334, 9.333333333333334, 9.333333333333334, 9.333333333333334], [32.66666666666666, 10.88888888888889, 10.88888888888889, 10.88888888888889, 10.88888888888889], [37.33333333333332, 12.444444444444445, 12.444444444444445, 12.444444444444445, 12.444444444444445], [41.999999999999986, 14.0, 14.0, 14.0, 14.0], [33.59999999999999, 11.2, 11.2, 11.2, 11.2], [25.19999999999999, 8.399999999999999, 8.399999999999999, 8.399999999999999, 8.399999999999999], [16.79999999999999, 5.599999999999998, 5.599999999999998, 5.599999999999998, 5.599999999999998], [8.39999999999999, 2.7999999999999976, 2.7999999999999976, 2.7999999999999976, 2.7999999999999976], [-1.0658141036401503e-14, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15], [-1.0658141036401503e-14, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15], [-1.0658141036401503e-14, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15], [-1.0658141036401503e-14, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [9.333333333333332, 3.111111111111111, 3.111111111111111, 3.111111111111111, 3.111111111111111], [13.999999999999998, 4.666666666666667, 4.666666666666667, 4.666666666666667, 4.666666666666667], [18.666666666666664, 6.222222222222222, 6.222222222222222, 6.222222222222222, 6.222222222222222], [23.33333333333333, 7.777777777777778, 7.777777777777778, 7.777777777777778, 7.777777777777778], [27.999999999999993, 9.333333333333334, 9.333333333333334, 9.333333333333334, 9.333333333333334], [32.66666666666666, 10.88888888888889, 10.88888888888889, 10.88888888888889, 10.88888888888889], [37.33333333333332, 12.444444444444445, 12.444444444444445, 12.444444444444445, 12.444444444444445], [41.999999999999986, 14.0, 14.0, 14.0, 14.0], [33.59999999999999, 11.2, 11.2, 11.2, 11.2], [25.19999999999999, 8.399999999999999, 8.399999999999999, 8.399999999999999, 8.399999999999999], [16.79999999999999, 5.599999999999998, 5.599999999999998, 5.599999999999998, 5.599999999999998], [8.39999999999999, 2.7999999999999976, 2.7999999999999976, 2.7999999999999976, 2.7999999999999976], [-1.0658141036401503e-14, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15], [-1.0658141036401503e-14, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15], [-1.0658141036401503e-14, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15], [-1.0658141036401503e-14, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15, -2.6645352591003757e-15]]
solarAllTransposed = [[0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.02180786419772134, 0.007918594026631155, 0.007598121466932286, 0.00785755453304973, 0.0073997192626350326], [0.9963984411487828, 0.33023339791518413, 0.3652548299484428, 0.33419528671828735, 0.3254005977751539], [1.1509744344261028, 0.3837440559522606, 0.39595400190649105, 0.3953778132852838, 0.4082591191418685], [1.8064601034850911, 0.5958663645190269, 0.6512208988936304, 0.6563921988512951, 0.6623180160574841], [4.165306851565079, 1.5009221795341479, 1.2876526484162756, 1.4176268897466668, 1.41562670521856], [5.803849520302269, 1.8759333971499705, 1.63951103880168, 1.753904654016115, 1.903459401289822], [4.594948480278264, 1.6457978116015544, 1.7847585479845012, 1.7101778150574178, 1.59031692996781], [6.18626071324736, 2.0167568382567573, 1.9469874545029089, 2.1616295102101346, 2.0628385320879588], [6.108232891123764, 1.9635370353123394, 1.9499388075072541, 1.8895748066521438, 1.739968758742219], [5.536205895474297, 2.0278335274349297, 1.7554089390567782, 1.8376381717920773, 1.9210875627664292], [4.849543075844584, 1.4587287253636674, 1.6502531459844016, 1.4283942351172532, 1.5151612113353208], [2.542742744559254, 0.8064178872860392, 0.8307617321493445, 0.8439795387931157, 0.8416497213963208], [0.5220744205834669, 0.17394656200626202, 0.16277584249706903, 0.17826452981725247, 0.18116484361026605], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.02231362517372497, 0.007928778406810366, 0.0073291488363084085, 0.008002362625578874, 0.008013338434675646], [1.007397923739057, 0.37297904341563587, 0.33955139563026876, 0.31945390431083326, 0.3664217738590594], [1.0667658518415442, 0.3785719113080719, 0.33212446569558957, 0.3315223232803358, 0.33266262310281314], [3.4860054012434833, 1.1193439257286002, 1.0445019368850903, 1.0610908004014896, 1.1529845091047335], [3.9444341048127822, 1.2296533587817464, 1.240922721664601, 1.3234844002145507, 1.2140475299725881], [5.078758001991692, 1.8988446107672117, 1.6622543242578296, 1.7238945648731547, 1.773354748351756], [6.558598889102438, 2.3777305572940874, 2.2849942826767613, 2.3513740881866827, 2.3300610673192406], [7.641310754802455, 2.4511864220739232, 2.558266826575028, 2.4721912210059935, 2.245526617084984], [6.789032188827468, 2.076719595971017, 2.331277805980687, 2.3223232822163222, 2.386507558439175], [5.716163056289812, 1.9993987314457051, 1.8492884268334988, 1.870909585786194, 2.1332220169504628], [4.5483210692362555, 1.594645619850973, 1.5587608684698113, 1.444937511845934, 1.4167591378179571], [2.5692157395033184, 0.8288313286774811, 0.819856558918866, 0.9039909002314187, 0.8289755907423666], [0.4669041818818022, 0.14096203574593683, 0.13863572285416123, 0.13952959786384447, 0.1446345131812008], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0]]
uAllTransposed = [[0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [-8.4, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003], [-8.4, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003], [-8.4, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003], [-8.4, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003], [-8.4, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [4.666666666666666, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556, 1.5555555555555556], [-8.4, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003], [-8.4, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003], [-8.4, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003], [-8.4, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003], [-8.4, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003, -2.8000000000000003], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0]]
voltageAllTransposed = [[1.0287055404946936, 0.9835408061928794, 0.9712944595053064, 0.9802950726537097, 0.9789374466639467, 0.9806558385979174, 0.9800639368709263], [1.032132725813748, 0.9782510101658383, 0.9882624272379632, 0.973674828780218, 0.967867274186252, 0.9751848907935087, 0.9746652959585245], [1.0286962024458883, 0.9800344736513648, 0.9766919108511564, 0.976057138760147, 0.9713037975541116, 0.9769716863131197, 0.9763785044687273], [1.0332407704031905, 0.9841389218608668, 0.9667592295968095, 0.9802601372740088, 0.9746913881875319, 0.9808730836650177, 0.9803032152289078], [1.021138564380775, 0.9869796019752525, 0.9809965300475437, 0.9832430477127637, 0.9788614356192249, 0.985693380624862, 0.9851316587130531], [1.0332067020769868, 0.9776220521456883, 0.9766256391090853, 0.9726525077365671, 0.9667932979230133, 0.9748757145244011, 0.9742243929651083], [1.0256148771534235, 0.9838343638923316, 0.9799742967437991, 0.9799205183316186, 0.9743851228465765, 0.9812399913463116, 0.9805755338196436], [1.0340499652488444, 0.9620485561760248, 0.9651039153919411, 0.9557626848842911, 0.9454722688342705, 0.9557980731328862, 0.9520159449749199], [1.0353854045981183, 0.9600174493250497, 0.9674586900044373, 0.9539973754364542, 0.9444591838530391, 0.953539602840681, 0.9498529473544516], [1.0254690784731255, 0.9657239720515169, 0.9744783761402304, 0.9613261558272276, 0.9556223583920627, 0.9594102623235696, 0.9559933512104916], [1.0285337273376496, 0.9651319141504083, 0.9839852683666832, 0.9601868162377365, 0.952880884383377, 0.9598905284783045, 0.9573164049322211], [1.0180338070187172, 0.9712656646525224, 0.976963779118795, 0.9679886781157442, 0.9650822419778585, 0.9669422456477327, 0.9649248386686022], [1.0261377888935685, 0.9654884869758663, 0.9783285588480773, 0.9608435238154662, 0.956022483501027, 0.9604334944140717, 0.958040553698725], [1.028955183316775, 0.9662797481776046, 0.9866917687034287, 0.9606663830102757, 0.9529499081832563, 0.9621476661863481, 0.9602528368219856], [1.0330540465895368, 0.9629798001172747, 0.9807071277773145, 0.9571646418296419, 0.9480898602941357, 0.9581728694614233, 0.9558864678682969], [1.0336410714904936, 0.9618764888691911, 0.9693047793855312, 0.9558640124064041, 0.9477053043002434, 0.9568286020293979, 0.9547616780668944], [0.9866401275006973, 0.9930548146021019, 1.0543009984261653, 0.9950646755486006, 1.00425583644881, 0.9983492503190603, 1.004689021588623], [1.0177737776331595, 0.9869849236565092, 1.0781352432570683, 0.9835099678146574, 0.9802187334388193, 0.9920294060197766, 0.9978463810226131], [1.0082304877926571, 1.0102939595934854, 1.0393345383310955, 1.0106713292341911, 1.0139497797551789, 1.0145802760690508, 1.0195418845345805], [1.0104544188587588, 1.009275811858425, 1.026866860813034, 1.009229007451976, 1.014879557433401, 1.0135830914701813, 1.018386921308558], [1.0198436609605488, 0.9985266268724547, 1.059605538968753, 0.9969995536388494, 0.9991274576822532, 1.002423382683181, 1.0072461960311334], [1.0352508875964925, 0.9755461539385156, 1.0055514964943515, 0.9703926458830925, 0.9647491124035076, 0.9726137977902735, 0.9717093009651108], [1.0300581027447469, 0.9797559351930444, 0.9743841717809586, 0.9755974986370722, 0.9699418972552531, 0.9767005243585959, 0.9758700600956851], [1.0280242009023441, 0.9823339849572927, 0.9737844222411186, 0.977799718988891, 0.9719757990976559, 0.9799172416854087, 0.9791247761195592], [1.036757362151927, 0.9819442692116197, 0.9632426378480731, 0.9768549297325702, 0.9703552540286619, 0.9789923626798808, 0.9782291021125361], [1.0322334933181323, 0.9781105159412171, 0.9858794038484261, 0.9734054685654593, 0.9677665066818679, 0.9749005592661314, 0.974027596155593], [1.0234683205773654, 0.9845838256007099, 0.9917551315347778, 0.9807046802987148, 0.9765316794226347, 0.9828823644899969, 0.9819826155889589], [1.010784826487804, 0.993851332161563, 0.9892151735121957, 0.9927355726612066, 0.9920413422599348, 0.9925292902192765, 0.9915726634398326], [1.0284692368669655, 0.9815658935397854, 1.0125678336564647, 0.9770384639990162, 0.9715307631330348, 0.9790453549859818, 0.9781499342315504], [1.0204689546726333, 0.9868284801951204, 1.0035517229115831, 0.9841161445753025, 0.9795310453273667, 0.984409043843684, 0.9835204866980557], [1.042732867943534, 0.973715496535625, 1.0214675250814143, 0.9672447587383544, 0.9572671320564663, 0.9708915941583475, 0.9699175842989343], [1.0433310052409412, 0.9569594718163078, 0.9554674829738656, 0.949352244285222, 0.9349225773515499, 0.9508289624763585, 0.9468580262529492], [1.0352168318237656, 0.9598189573729592, 0.9402247616061061, 0.9535775899379936, 0.9447393321054983, 0.9536990584428724, 0.9497682848931007], [1.0326141498231025, 0.9636046526603687, 0.990646217959557, 0.9572357158352239, 0.9480594011366712, 0.9585839137538681, 0.9552453775044912], [1.0340386833726183, 0.9637340426278385, 0.9942126715096915, 0.9571599708015663, 0.9466366669430043, 0.9592414239835245, 0.9560040819923296], [1.025709507010128, 0.9695614192579051, 0.9795278193485429, 0.9640752244670312, 0.9566165470293487, 0.9662007310003761, 0.963554884249493], [1.0234489034369962, 0.9696683579786576, 0.9903976243844477, 0.9649614033633965, 0.9594446785697806, 0.9660534403028628, 0.9639367672895183], [1.0208790244873824, 0.97114104934985, 0.9786013684884023, 0.9669072296056972, 0.9624414331953179, 0.9676007575311641, 0.965357897748238], [1.0153033293667741, 0.9764494134989811, 0.9746584197147021, 0.974154680138446, 0.9685134866142283, 0.9724786490803581, 0.9703466549877765], [1.0097029530508619, 0.9806106216344188, 0.973414404273609, 0.9786057749657225, 0.9748844757855762, 0.9776337314086404, 0.975290845477164], [0.9809723176250003, 0.9932700111658492, 1.0530301052987754, 0.9952676408489716, 1.0003769393139879, 0.9999710543209825, 1.0055672871279828], [0.9994246702153329, 1.0020394797127072, 1.0492997245700546, 1.0021179083151686, 1.0065411951607197, 1.0082445640604274, 1.013410731886977], [1.001154269258599, 1.0044888879413292, 1.0467678908104747, 1.0054490439359236, 1.0127507596554093, 1.0089984156957192, 1.013566217588116], [1.005770334297396, 1.0104795224953795, 1.0337190056875316, 1.0113792949872735, 1.0183290583907052, 1.014911678076373, 1.01926356286972], [1.006090909934006, 1.0093119204055365, 1.0437509554780862, 1.0093947041182294, 1.0135579745966203, 1.014628268965081, 1.019092197010929], [1.0253599955064794, 0.995990462362132, 0.9746400044935207, 0.9928850612117441, 0.9881662976189657, 0.9945749102278181, 0.9933900243647483], [1.0291556577574519, 0.9952818644341396, 0.9708443422425481, 0.992730632457794, 0.990771258880919, 0.9927095068293358, 0.991528246811716], [1.0201664932117271, 0.988676177663197, 1.0063254136846873, 0.9852424125693283, 0.9798335067882727, 0.9873496109196308, 0.9861812586842187]]


$(document).ready(function(ns) {
    var onLoad = function() {
        buildCharts(netPowerAllTransposed, 'net-power-all', {title: 'Net Power for Each Node'});
        buildCharts(solarAllTransposed, 'solar-all', {title: 'Solar Generation for Each Node'});
        buildCharts(qAllTransposed, 'q-all', {title: 'State of Charge for Each Node'});
        buildCharts(uAllTransposed, 'u-all', {title: 'Charging Action for Each Node'});
        buildCharts(voltageAllTransposed, 'voltage-all', {title: 'Voltage for Each Node'});
    },

    buildCharts = function(dataSource, divId, layout) {
        var d00 = getArrayValues(0, dataSource),
            d01 = getArrayValues(1, dataSource),
            d02 = getArrayValues(2, dataSource),
            d03 = getArrayValues(3, dataSource),
            d04 = getArrayValues(4, dataSource),
            d05, d06,
            trace00, trace01, trace02, trace03, trace04, trace05, trace06,
            plotlyDataSource;

        if (divId === 'net-power-all' || divId === 'voltage-all') {
            d05 = getArrayValues(5, dataSource);
            d06 = getArrayValues(6, dataSource);
            trace00 = {
                type: "scatter",
                mode: "lines",
                name: 'Substation',
                x: timeFrame,
                y: d00,
                line: {color: '#000000'}
            };
            trace01 = {
                type: "scatter",
                mode: "lines",
                name: 'Transformer',
                x: timeFrame,
                y: d01,
                line: {color: '#7F7123'}
            };
            trace02 = {
                type: "scatter",
                mode: "lines",
                name: 'Building',
                x: timeFrame,
                y: d02,
                line: {color: '#17BECF'}
            };
            trace03 = {
                type: "scatter",
                mode: "lines",
                name: 'Home One',
                x: timeFrame,
                y: d03,
                line: {color: '#7F7F7F'}
            };
            trace04 = {
                type: "scatter",
                mode: "lines",
                name: 'Home Two',
                x: timeFrame,
                y: d04,
                line: {color: '#FFFF00'}
            };
            trace05 = {
                type: "scatter",
                mode: "lines",
                name: 'Home Three',
                x: timeFrame,
                y: d05,
                line: {color: '#FF0000'}
            };
            trace06 = {
                type: "scatter",
                mode: "lines",
                name: 'Home Four',
                x: timeFrame,
                y: d06,
                line: {color: '#008000'}
            };
            plotlyDataSource = [trace00, trace01, trace02, trace03, trace04, trace05, trace06];
        } else {
            trace00 = {
                type: "scatter",
                mode: "lines",
                name: 'Building',
                x: timeFrame,
                y: d00,
                line: {color: '#17BECF'}
            };
            trace01 = {
                type: "scatter",
                mode: "lines",
                name: 'Home One',
                x: timeFrame,
                y: d01,
                line: {color: '#7F7F7F'}
            };
            trace02 = {
                type: "scatter",
                mode: "lines",
                name: 'Home Two',
                x: timeFrame,
                y: d02,
                line: {color: '#FFFF00'}
            };
            trace03 = {
                type: "scatter",
                mode: "lines",
                name: 'Home Three',
                x: timeFrame,
                y: d03,
                line: {color: '#FF0000'}
            };
            trace04 = {
                type: "scatter",
                mode: "lines",
                name: 'Home Four',
                x: timeFrame,
                y: d04,
                line: {color: '#008000'}
            };
            plotlyDataSource = [trace00, trace01, trace02, trace03, trace04];
        }

        Plotly.newPlot(divId, plotlyDataSource, layout);
    },

    getArrayValues = function(position, dataSource) {
        // TODO: add boundary check to position param
        return _.map(dataSource, function(v) {
            return v[position];
        });
    };

    onLoad();
}(plotNoControl));