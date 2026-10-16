package su.xash.cs16client;

import android.app.Application;
import android.content.Context;
import android.util.Log;

public class CS16Application extends Application {
    private static final String TAG = "CS16App";

    @Override
    protected void attachBaseContext(Context base) {
        super.attachBaseContext(base);
        try {
            CS16CrashHandler.installAll(base);
            Log.i(TAG, "crash handlers installed");
        } catch (Throwable x) {
            Log.e(TAG, "installAll failed", x);
        }
    }

    @Override
    public void onCreate() {
        super.onCreate();
        Log.i(TAG, "app onCreate");
        try {
            CS16CrashHandler.installAll(this);
        } catch (Throwable x) {
            Log.e(TAG, "onCreate failed", x);
        }
    }
}
