package su.xash.cs16client;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

public class MainActivity extends Activity {
    private static final String TAG = "CS16Main";
    private static final long START_TIMEOUT_MS = 5000L;
    private boolean launched = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        CS16CrashHandler.install(this);
        Log.i(TAG, "onCreate, package=" + getPackageName());

        try {
            Intent i = new Intent();
            i.setClassName(getPackageName(), "su.xash.engine.XashActivity");
            i.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            i.putExtra("gamedir", "cstrike");
            i.putExtra("gamelibdir", getApplicationInfo().nativeLibraryDir);
            i.putExtra("argv", "-dev 2 -log -dll @yapb");
            i.putExtra("package", getPackageName());
            startActivity(i);
            launched = true;
            Log.i(TAG, "XashActivity startActivity ok");
            watchStartup();
        } catch (Throwable e) {
            Log.e(TAG, "startActivity failed", e);
            CS16CrashHandler.report(this, "startactivity_failed", "MainActivity failed to launch XashActivity", e);
            finish();
            return;
        }
        finish();
    }

    private void watchStartup() {
        new Handler(Looper.getMainLooper()).postDelayed(new Runnable() {
            @Override
            public void run() {
                if (!XashStartupTracker.getInstance().isXashStarted()) {
                    Log.e(TAG, "XashActivity did not start within timeout");
                    CS16CrashHandler.report(MainActivity.this, "xash_start_timeout",
                        "XashActivity did not call onCreate within " + START_TIMEOUT_MS + "ms. Engine may have crashed on load.");
                } else {
                    Log.i(TAG, "XashActivity started ok");
                }
            }
        }, START_TIMEOUT_MS);
    }
}
