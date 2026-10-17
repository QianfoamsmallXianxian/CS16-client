package su.xash.cs16client;

import android.app.Application;
import android.content.Context;
import android.util.Log;

public class CS16Application extends Application {
    @Override
    protected void attachBaseContext(Context base) {
        super.attachBaseContext(base);
        CS16CrashHandler.install(base);
    }
    @Override
    public void onCreate() {
        super.onCreate();
        CS16CrashHandler.install(this);
    }
}
