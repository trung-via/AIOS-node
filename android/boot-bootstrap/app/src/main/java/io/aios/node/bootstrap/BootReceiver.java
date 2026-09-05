package io.aios.node.bootstrap;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import android.util.Log;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.TimeZone;

/**
 * Non-exported BroadcastReceiver triggered by Android BOOT_COMPLETED.
 *
 * Performs exactly one fixed dispatch to Termux RunCommandService using the compile-time
 * constant bootstrap script path. Contains no loop, retry, worker, alarm, or polling mechanism.
 */
public class BootReceiver extends BroadcastReceiver {

    private static final String TAG = "AiosBootReceiver";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (context == null || intent == null) {
            return;
        }

        String action = intent.getAction();
        if (!Intent.ACTION_BOOT_COMPLETED.equals(action)) {
            Log.w(TAG, "Ignoring unexpected action: " + action);
            return;
        }

        String nowIso = formatIso8601(new Date());
        SharedPreferences prefs = context.getSharedPreferences(
                BootstrapContract.PREFS_NAME, Context.MODE_PRIVATE);

        // Record boot reception timestamp
        prefs.edit().putString(BootstrapContract.KEY_LAST_BOOT_RECEIVED_AT, nowIso).apply();

        // Check required permission
        if (context.checkSelfPermission(BootstrapContract.PERMISSION_RUN_COMMAND)
                != PackageManager.PERMISSION_GRANTED) {
            Log.e(TAG, "RUN_COMMAND permission not granted; cannot dispatch to Termux");
            prefs.edit()
                    .putString(BootstrapContract.KEY_LAST_DISPATCH_TIME, nowIso)
                    .putString(BootstrapContract.KEY_LAST_DISPATCH_RESULT,
                            BootstrapContract.RESULT_PERMISSION_DENIED)
                    .putString(BootstrapContract.KEY_LAST_ERROR, "com.termux.permission.RUN_COMMAND not granted")
                    .apply();
            return;
        }

        Intent runIntent = BootstrapContract.createFixedRunCommandIntent();

        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(runIntent);
            } else {
                context.startService(runIntent);
            }

            prefs.edit()
                    .putString(BootstrapContract.KEY_LAST_DISPATCH_TIME, nowIso)
                    .putString(BootstrapContract.KEY_LAST_DISPATCH_RESULT,
                            BootstrapContract.RESULT_SUCCESS)
                    .remove(BootstrapContract.KEY_LAST_ERROR)
                    .apply();
            Log.i(TAG, "Dispatched bootstrap intent to Termux RunCommandService");
        } catch (Exception e) {
            Log.e(TAG, "Failed to dispatch to Termux RunCommandService", e);
            prefs.edit()
                    .putString(BootstrapContract.KEY_LAST_DISPATCH_TIME, nowIso)
                    .putString(BootstrapContract.KEY_LAST_DISPATCH_RESULT,
                            BootstrapContract.RESULT_ERROR)
                    .putString(BootstrapContract.KEY_LAST_ERROR, e.getClass().getSimpleName() + ": " + e.getMessage())
                    .apply();
        }
    }

    private static String formatIso8601(Date date) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US);
        sdf.setTimeZone(TimeZone.getTimeZone("UTC"));
        return sdf.format(date);
    }
}
