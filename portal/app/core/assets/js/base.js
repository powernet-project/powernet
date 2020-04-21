$(document).ready(function() {
    let isSidebarExpanded = localStorage.getItem("isSidebarExpanded");
	// sidebar expanded by default
    if (isSidebarExpanded === null) {
        // value hasn't been set yet
        localStorage.setItem("isSidebarExpanded", "true");
    }
	if (isSidebarExpanded === "false") {
		// false means not expaded
        $('#sidebar').toggleClass('active');
    }
});

function toggleSideBar() {
	$('#sidebar').toggleClass('active');
	let isSidebarExpanded = localStorage.getItem("isSidebarExpanded") === "true";
	localStorage.setItem("isSidebarExpanded", (!isSidebarExpanded).toString());
}
