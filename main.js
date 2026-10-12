// Gym Management System - Interactive UI Scripts

document.addEventListener('DOMContentLoaded', () => {

    // --- Dynamic Expiration Date Auto-Calculation ---
    const startDateInput = document.getElementById('start_date');
    const planSelect = document.getElementById('membership_plan');
    const expDatePreview = document.getElementById('expiration_date_preview');
    const expDateInput = document.getElementById('expiration_date');

    function updateExpirationPreview() {
        if (!startDateInput || !planSelect) return;

        const startDateVal = startDateInput.value;
        const planVal = planSelect.value;

        if (!startDateVal || !planVal) return;

        fetch('/api/calculate-expiration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start_date: startDateVal,
                plan: planVal
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.expiration_date) {
                if (expDatePreview) expDatePreview.value = data.expiration_date;
                if (expDateInput) expDateInput.value = data.expiration_date;
            }
        })
        .catch(err => console.error('Error calculating expiration date:', err));
    }

    if (startDateInput && planSelect) {
        startDateInput.addEventListener('change', updateExpirationPreview);
        planSelect.addEventListener('change', updateExpirationPreview);
    }

    // --- Confirmation Modal / Prompt for Deletion ---
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const name = form.getAttribute('data-member-name') || 'this member';
            if (!confirm(`Are you sure you want to delete member record for "${name}"? This action cannot be undone.`)) {
                e.preventDefault();
            }
        });
    });

    // --- Dynamic Member Info Autofill on Payment Page ---
    const paymentMemberSelect = document.getElementById('payment_member_select');
    const currentPlanBadge = document.getElementById('current_plan_badge');
    const currentStatusBadge = document.getElementById('current_status_badge');
    const currentExpDate = document.getElementById('current_exp_date');

    if (paymentMemberSelect) {
        paymentMemberSelect.addEventListener('change', (e) => {
            const selectedOpt = e.target.selectedOptions[0];
            if (selectedOpt && selectedOpt.dataset) {
                const plan = selectedOpt.dataset.plan || '--';
                const status = selectedOpt.dataset.status || '--';
                const exp = selectedOpt.dataset.exp || '--';

                if (currentPlanBadge) currentPlanBadge.textContent = plan;
                if (currentExpDate) currentExpDate.textContent = exp;
                if (currentStatusBadge) {
                    currentStatusBadge.textContent = status;
                    currentStatusBadge.className = 'badge ' + (status === 'Active' ? 'badge-active' : 'badge-expired');
                }
            }
        });
    }

    // --- Live Instant Search Filtering ---
    function setupLiveFilter(inputId, tableSelector, rowSelector) {
        const input = document.getElementById(inputId);
        const table = document.querySelector(tableSelector);
        if (!input || !table) return;

        input.addEventListener('input', () => {
            const filter = input.value.trim().toLowerCase();
            const rows = table.querySelectorAll(rowSelector);

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (!filter || text.includes(filter)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Wire up live search for search.html and members.html
    setupLiveFilter('searchInput', '#membersTable', 'tbody tr');
    setupLiveFilter('memberListSearch', '#memberDirectoryTable', 'tbody tr');

});
