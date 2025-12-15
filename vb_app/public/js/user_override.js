frappe.ui.form.on('User', {
    setup: function(frm) {
        // Check if the user is NEITHER Administrator NOR System Manager
        // If they are regular users, we hide the Roles immediately via CSS
        if (frappe.session.user !== 'Administrator' && !frappe.user.has_role('System Manager')) {
            
            $("<style>")
                .prop("type", "text/css")
                .html(`
                    div[data-fieldname='roles'] {
                        display: none !important;
                    }
                    div[data-fieldname='sb_roles'] { /* Often the section break for roles */
                        display: none !important;
                    }
                    div[data-fieldname='block_modules'] {
                        display: none !important;
                    }
                `)
                .appendTo("head");
        }
    },

    refresh: function(frm) {
        // If the user is restricted (Not Admin/Sys Mgr), ensure Role Profile is editable
        // This allows them to assign profiles (like "HR") without seeing the raw roles
        if (frappe.session.user !== 'Administrator' && !frappe.user.has_role('System Manager')) {
            frm.set_df_property('role_profile_name', 'read_only', 0);
        }
    }
});