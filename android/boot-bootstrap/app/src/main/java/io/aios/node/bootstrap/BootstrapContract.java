package io.aios.node.bootstrap;

import android.content.ComponentName;
import android.content.Intent;

/**
 * Immutable bootstrap contract constants and fixed dispatch factory.
 *
 * NODE-003B: Defines the strictly bounded boundary between the standalone Android
 * cold-boot helper and Termux RunCommandService.
 */
public final class BootstrapContract {

    private BootstrapContract() {
        // Enforce non-instantiability
    }

    // Termux RunCommandService contract
    public static final String TERMUX_PACKAGE = "com.termux";
    public static final String TERMUX_SERVICE_CLASS = "com.termux.app.RunCommandService";
    public static final String ACTION_RUN_COMMAND = "com.termux.RUN_COMMAND";

    // Termux RUN_COMMAND intent extras
    public static final String EXTRA_RUN_COMMAND_PATH = "com.termux.RUN_COMMAND_PATH";
    public static final String EXTRA_RUN_COMMAND_ARGUMENTS = "com.termux.RUN_COMMAND_ARGUMENTS";
    public static final String EXTRA_RUN_COMMAND_RUNNER = "com.termux.RUN_COMMAND_RUNNER";
    public static final String EXTRA_RUN_COMMAND_BACKGROUND = "com.termux.RUN_COMMAND_BACKGROUND";

    // Runner value for non-interactive background execution
    public static final String RUNNER_APP_SHELL = "app-shell";

    // Immutable compile-time constant bootstrap script path
    public static final String BOOTSTRAP_SCRIPT_PATH =
            "/data/data/com.termux/files/home/.aios-node/bootstrap/start-services.sh";

    // Required permissions
    public static final String PERMISSION_RUN_COMMAND = "com.termux.permission.RUN_COMMAND";
    public static final String PERMISSION_RECEIVE_BOOT_COMPLETED =
            "android.permission.RECEIVE_BOOT_COMPLETED";

    // SharedPreferences keys for bounded operational diagnostics only (never engineering truth)
    public static final String PREFS_NAME = "bootstrap_diagnostics";
    public static final String KEY_LAST_BOOT_RECEIVED_AT = "last_boot_received_at";
    public static final String KEY_LAST_DISPATCH_TIME = "last_dispatch_time";
    public static final String KEY_LAST_DISPATCH_RESULT = "last_dispatch_result";
    public static final String KEY_LAST_ERROR = "last_error";

    public static final String RESULT_SUCCESS = "DISPATCHED";
    public static final String RESULT_PERMISSION_DENIED = "PERMISSION_DENIED";
    public static final String RESULT_ERROR = "FAILED";

    /**
     * Creates the immutable, fixed RunCommand Intent.
     * No parameterization is permitted; command path, arguments, component, and action
     * are strictly compile-time constants.
     */
    public static Intent createFixedRunCommandIntent() {
        Intent intent = new Intent(ACTION_RUN_COMMAND);
        intent.setComponent(new ComponentName(TERMUX_PACKAGE, TERMUX_SERVICE_CLASS));
        intent.putExtra(EXTRA_RUN_COMMAND_PATH, BOOTSTRAP_SCRIPT_PATH);
        intent.putExtra(EXTRA_RUN_COMMAND_ARGUMENTS, new String[0]);
        intent.putExtra(EXTRA_RUN_COMMAND_RUNNER, RUNNER_APP_SHELL);
        intent.putExtra(EXTRA_RUN_COMMAND_BACKGROUND, true);
        return intent;
    }
}
