// session timer in topbar
(function() {
    var start = Date.now();
    var el = document.getElementById('session-timer');
    if (!el) return;

    setInterval(function() {
        var elapsed = Math.floor((Date.now() - start) / 1000);
        var h = Math.floor(elapsed / 3600);
        var m = Math.floor((elapsed % 3600) / 60);
        var s = elapsed % 60;
        el.textContent = 'SESSION: ' +
            String(h).padStart(2,'0') + ':' +
            String(m).padStart(2,'0') + ':' +
            String(s).padStart(2,'0');
    }, 1000);
})();

// modal toggle
function toggleModal(id) {
    var el = document.getElementById(id);
    if (!el) return;
    el.style.display = el.style.display === 'none' ? 'flex' : 'none';
}

// close modal when clicking outside
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.style.display = 'none';
    }
});

// auto-dismiss flash messages after 5s
setTimeout(function() {
    document.querySelectorAll('.flash').forEach(function(el) {
        el.style.transition = 'opacity 0.5s';
        el.style.opacity = '0';
        setTimeout(function() { el.remove(); }, 500);
    });
}, 5000);
