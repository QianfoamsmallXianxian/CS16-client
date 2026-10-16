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
            CS16CrashHandler.install((android.app.Activity) null);
            Log.i(TAG, "early handler installed");
        } catch (Throwable x) {
            Log.e(TAG, "early handler failed", x);
        }
    }

    @Override
    public void onCreate() {
        super.onCreate();
        Log.i(TAG, "app onCreate");
        try {
            Thread.setDefaultUncaughtExceptionHandler(
                new CS16CrashHandler(this, Thread.getDefaultUncaughtExceptionHandler()));
            Log.i(TAG, "handler installed in Application");
        } catch (Throwable x) {
            Log.e(TAG, "app handler failed", x);
        }
    }
}
