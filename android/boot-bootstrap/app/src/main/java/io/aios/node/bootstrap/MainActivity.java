package io.aios.node.bootstrap;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

/**
 * One-time setup and diagnostic Activity for AIOS Boot Bootstrap.
 *
 * Bounded UI only: reports and requests RUN_COMMAND permission, displays
 * host-local boot-dispatch diagnostics, and describes qualification prerequisites.
 * Exposes no generic command execution, text input, shell, or remote-control surface.
 */
public class MainActivity extends Activity {

    private static final int REQUEST_CODE_PERMISSION = 1001;

    private TextView permissionStatusView;
    private Button requestPermissionButton;
    private TextView lastBootReceivedView;
    private TextView lastDispatchTimeView;
    private TextView lastDispatchResultView;
    private TextView lastErrorView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        ScrollView scrollView = new ScrollView(this);
        scrollView.setLayoutParams(new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));
        scrollView.setPadding(32, 32, 32, 32);

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setLayoutParams(new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));

        // Title
        TextView titleView = new TextView(this);
        titleView.setText(getString(R.string.title_bootstrap_setup));
        titleView.setTextSize(20f);
        titleView.setPadding(0, 0, 0, 24);
        layout.addView(titleView);

        // Section: Permission
        TextView permHeader = new TextView(this);
        permHeader.setText(getString(R.string.header_permission));
        permHeader.setTextSize(16f);
        permHeader.setPadding(0, 8, 0, 8);
        layout.addView(permHeader);

        permissionStatusView = new TextView(this);
        permissionStatusView.setPadding(0, 0, 0, 8);
        layout.addView(permissionStatusView);

        requestPermissionButton = new Button(this);
        requestPermissionButton.setText(getString(R.string.btn_request_permission));
        requestPermissionButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                requestRunCommandPermission();
            }
        });
        layout.addView(requestPermissionButton);

        // Section: Diagnostics
        TextView diagHeader = new TextView(this);
        diagHeader.setText(getString(R.string.header_diagnostics));
        diagHeader.setTextSize(16f);
        diagHeader.setPadding(0, 24, 0, 8);
        layout.addView(diagHeader);

        lastBootReceivedView = new TextView(this);
        layout.addView(lastBootReceivedView);

        lastDispatchTimeView = new TextView(this);
        layout.addView(lastDispatchTimeView);

        lastDispatchResultView = new TextView(this);
        layout.addView(lastDispatchResultView);

        lastErrorView = new TextView(this);
        layout.addView(lastErrorView);

        // Section: Host Qualification Requirements
        TextView reqHeader = new TextView(this);
        reqHeader.setText(getString(R.string.header_prerequisites));
        reqHeader.setTextSize(16f);
        reqHeader.setPadding(0, 24, 0, 8);
        layout.addView(reqHeader);

        TextView reqText = new TextView(this);
        reqText.setText(getString(R.string.text_prerequisites));
        reqText.setPadding(0, 0, 0, 24);
        layout.addView(reqText);

        scrollView.addView(layout);
        setContentView(scrollView);
    }

    @Override
    protected void onResume() {
        super.onResume();
        refreshDisplay();
    }

    private void requestRunCommandPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            requestPermissions(
                    new String[]{BootstrapContract.PERMISSION_RUN_COMMAND},
                    REQUEST_CODE_PERMISSION);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_CODE_PERMISSION) {
            refreshDisplay();
        }
    }

    private void refreshDisplay() {
        boolean granted = checkSelfPermission(BootstrapContract.PERMISSION_RUN_COMMAND)
                == PackageManager.PERMISSION_GRANTED;

        if (granted) {
            permissionStatusView.setText(getString(R.string.status_perm_granted));
            requestPermissionButton.setEnabled(false);
        } else {
            permissionStatusView.setText(getString(R.string.status_perm_not_granted));
            requestPermissionButton.setEnabled(true);
        }

        SharedPreferences prefs = getSharedPreferences(
                BootstrapContract.PREFS_NAME, Context.MODE_PRIVATE);

        String lastBoot = prefs.getString(BootstrapContract.KEY_LAST_BOOT_RECEIVED_AT, "none");
        String lastDispatch = prefs.getString(BootstrapContract.KEY_LAST_DISPATCH_TIME, "none");
        String lastResult = prefs.getString(BootstrapContract.KEY_LAST_DISPATCH_RESULT, "none");
        String lastErr = prefs.getString(BootstrapContract.KEY_LAST_ERROR, "none");

        lastBootReceivedView.setText(getString(R.string.label_last_boot, lastBoot));
        lastDispatchTimeView.setText(getString(R.string.label_last_dispatch, lastDispatch));
        lastDispatchResultView.setText(getString(R.string.label_last_result, lastResult));
        lastErrorView.setText(getString(R.string.label_last_error, lastErr));
    }
}
