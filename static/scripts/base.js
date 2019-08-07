let mobileNav = null;
document.addEventListener('DOMContentLoaded', function () {
    mobileNav = M.Sidenav.init(document.querySelector('#mobile-nav'), {edge: "left", draggable: "true", preventScrolling: true});
});