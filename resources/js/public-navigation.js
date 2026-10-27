document.addEventListener('click', (event) => {
    const link = event.target.closest('a[data-release-link]');
    if (!link) return;
    const target = new URL(link.href);
    const current = new URL(location.href);
    for (const key of ['release_id', 'analysis_run_id']) {
        if (current.searchParams.has(key)) target.searchParams.set(key, current.searchParams.get(key));
    }
    link.href = target.href;
});
