var toggle = 1;

$(document).ready(function() {
	if(localStorage.getItem("toggle") == 0){
		toggleSideBar();
	}
});

function toggleSideBar() {
	$('#sidebar').toggleClass('active');
	if (toggle === 1) {
		toggle = 0;
	}
	else {
		toggle = 1;
	}
	localStorage.setItem("toggle", toggle);
}
