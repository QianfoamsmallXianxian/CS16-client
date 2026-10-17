package su.xash.cs16client;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class CS16CrashHandler implements Thread.UncaughtExceptionHandler {
    private final Context ctx;
    private final Thread.UncaughtExceptionHandler prev;

    public CS16CrashHandler(Context ctx, Thread.UncaughtExceptionHandler prev) {
        this.ctx = ctx != null ? ctx.getApplicationContext() : null;
        this.prev = prev;
    }

    public static void install(Activity a) {
        try {
            Context ctx = a != null ? a.getApplicationContext() : null;
            Thread.setDefaultUncaughtExceptionHandler(
                new CS16CrashHandler(ctx, Thread.getDefaultUncaughtExceptionHandler()));
        } catch (Throwable x) {}
    }

    public static void install(Context ctx) {
        try {
            Thread.setDefaultUncaughtExceptionHandler(
                new CS16CrashHandler(ctx, Thread.getDefaultUncaughtExceptionHandler()));
        } catch (Throwable x) {}
    }

    @Override
    public void uncaughtException(Thread t, Throwable e) {
        StringWriter sw = new StringWriter();
        e.printStackTrace(new PrintWriter(sw));
        String stackTrace = sw.toString();

        try {
            File dir = new File("/sdcard/CS16Crash");
            if (!dir.exists()) dir.mkdirs();
            FileWriter w = new FileWriter(new File(dir, "crash.txt"));
            w.write(stackTrace);
            w.close();
        } catch (Throwable ignored) {}

        if (ctx != null) {
            Intent intent = new Intent(ctx, CrashDisplayActivity.class);
            intent.putExtra("error_msg", stackTrace);
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
            ctx.startActivity(intent);
        }

        if (prev != null && prev != this) {
            prev.uncaughtException(t, e);
        } else {
            android.os.Process.killProcess(android.os.Process.myPid());
            System.exit(10);
        }
    }
}
