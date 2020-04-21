var toggle = 1;

$(document).ready(function() {
    let isSidebarExpanded = localStorage.getItem("isSidebarExpanded")
    if (isSidebarExpanded === null) {
        // value hasn't been set yet
        localStorage.setItem("isSidebarExpanded", "true");
    } else {
        toggleSideBar();
    }
});

function toggleSideBar() {
	$('#sidebar').toggleClass('active');
	let isSidebarExpanded = localStorage.getItem("isSidebarExpanded") === "true"
	localStorage.setItem("toggle", (!isSidebarExpanded).toString());
}
