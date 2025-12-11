// apps/vb_app/vb_app/public/js/custom_request.js

// Save the original function in case we need it
const original_call = frappe.request.call;

frappe.request.call = function (opts) {
    // We wrap the original error callback to inject your logic
    const original_error_callback = opts.error_callback;

    opts.error_callback = function (xhr) {
        if (xhr.status === 403) {
             // YOUR CUSTOM LOGIC HERE
             let error_msg = "";
             if (xhr.responseJSON && xhr.responseJSON._error_message) {
                error_msg = xhr.responseJSON._error_message;
             }

             // Redirect logic
             if (frappe.session.user !== "Guest" && error_msg.includes("Access Denied")) {
                 window.location.href = "/app"; // or wherever you want them to go
                 return;
             }
        }

        // Run standard Frappe error handling if we didn't redirect
        if (original_error_callback) {
            original_error_callback(xhr);
        }
    };

    // Execute the actual call
    return original_call(opts);
};