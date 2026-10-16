package su.xash.cs16client;

import android.app.Activity;
import android.content.Context;
import android.os.Build;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileWriter;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class CS16CrashHandler implements Thread.UncaughtExceptionHandler {
    private static final String TAG = "CS16Crash";
    private static final String DIR_NAME = "CS16Crash";
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
            Log.i(TAG, "handler installed");
        } catch (Throwable x) {
            Log.e(TAG, "install failed", x);
        }
    }

    public static void install(Context ctx) {
        try {
            Thread.setDefaultUncaughtExceptionHandler(
                new CS16CrashHandler(ctx, Thread.getDefaultUncaughtExceptionHandler()));
            Log.i(TAG, "handler installed (ctx)");
        } catch (Throwable x) {
            Log.e(TAG, "install failed", x);
        }
    }

    @Override
    public void uncaughtException(Thread t, Throwable e) {
        try {
            dump(ctx, t, e, "uncaught");
        } catch (Throwable x) {
        }
        if (prev != null) {
            prev.uncaughtException(t, e);
        }
    }

    public static void report(Context ctx, String kind, String message, Throwable e) {
        try {
            dumpCustom(ctx, kind, message, e);
        } catch (Throwable x) {
        }
    }

    public static void report(Context ctx, String kind, String message) {
        report(ctx, kind, message, null);
    }

    private static File getDir(Context ctx) {
        try {
            File sd = Environment.getExternalStorageDirectory();
            if (sd != null) {
                File d = new File(sd, DIR_NAME);
                if (!d.exists()) d.mkdirs();
                if (d.canWrite()) return d;
            }
        } catch (Throwable x) {
        }
        try {
            File d = new File("/sdcard/" + DIR_NAME);
            if (!d.exists()) d.mkdirs();
            if (d.canWrite()) return d;
        } catch (Throwable x) {
        }
        if (ctx != null) {
            File d = new File(ctx.getFilesDir(), DIR_NAME);
            if (!d.exists()) d.mkdirs();
            return d;
        }
        return new File("/data/local/tmp/" + DIR_NAME);
    }

    private static void dump(Context ctx, Thread t, Throwable e, String kind) {
        String ts = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(new Date());
        File dir = getDir(ctx);
        File out = new File(dir, "CS16_crash_" + kind + "_" + ts + ".log");
        FileWriter w = null;
        try {
            w = new FileWriter(out);
            w.write("=== CS16 Crash Report ===\n");
            w.write("time: " + new Date() + "\n");
            w.write("kind: " + kind + "\n");
            w.write("thread: " + (t != null ? t.getName() : "?") + "\n");
            w.write("device: " + Build.MANUFACTURER + " " + Build.MODEL + "\n");
            w.write("android: " + Build.VERSION.RELEASE + " (API " + Build.VERSION.SDK_INT + ")\n");
            String abi = "?";
            try {
                if (Build.SUPPORTED_ABIS != null && Build.SUPPORTED_ABIS.length > 0) abi = Build.SUPPORTED_ABIS[0];
            } catch (Throwable x) {}
            w.write("abi: " + abi + "\n");
            if (ctx != null) {
                try {
                    w.write("package: " + ctx.getPackageName() + "\n");
                    w.write("nativeLibDir: " + ctx.getApplicationInfo().nativeLibraryDir + "\n");
                } catch (Throwable x) {}
            }
            w.write("\n=== Stack ===\n");
            if (e != null) {
                StringWriter sw = new StringWriter();
                e.printStackTrace(new PrintWriter(sw));
                w.write(sw.toString());
            } else {
                w.write("(no throwable)\n");
            }
            w.write("\n=== Logcat (last 300) ===\n");
            try {
                Process p = Runtime.getRuntime().exec(new String[]{"logcat", "-d", "-t", "300", "-v", "threadtime"});
                BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()));
                String ln;
                int n = 0;
                while ((ln = r.readLine()) != null && n < 300) {
                    w.write(ln);
                    w.write("\n");
                    n++;
                }
                r.close();
            } catch (Throwable x) {
                w.write("(logcat unavailable)\n");
            }
            w.write("\n=== End ===\n");
            w.flush();
            Log.i(TAG, "crash written: " + out.getAbsolutePath());
        } catch (Throwable x) {
            Log.e(TAG, "dump failed", x);
        } finally {
            if (w != null) {
                try { w.close(); } catch (Throwable x) {}
            }
        }
    }

    private static void dumpCustom(Context ctx, String kind, String message, Throwable e) {
        String ts = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(new Date());
        File dir = getDir(ctx);
        File out = new File(dir, "CS16_bug_" + kind + "_" + ts + ".log");
        FileWriter w = null;
        try {
            w = new FileWriter(out);
            w.write("=== CS16 Bug Report ===\n");
            w.write("time: " + new Date() + "\n");
            w.write("kind: " + kind + "\n");
            w.write("message: " + message + "\n");
            w.write("device: " + Build.MANUFACTURER + " " + Build.MODEL + "\n");
            w.write("android: " + Build.VERSION.RELEASE + " (API " + Build.VERSION.SDK_INT + ")\n");
            if (ctx != null) {
                try {
                    w.write("package: " + ctx.getPackageName() + "\n");
                } catch (Throwable x) {}
            }
            w.write("\n=== Stack ===\n");
            if (e != null) {
                StringWriter sw = new StringWriter();
                e.printStackTrace(new PrintWriter(sw));
                w.write(sw.toString());
            } else {
                w.write("(no throwable)\n");
            }
            w.write("\n=== End ===\n");
            w.flush();
            Log.i(TAG, "bug written: " + out.getAbsolutePath());
        } catch (Throwable x) {
        } finally {
            if (w != null) {
                try { w.close(); } catch (Throwable x) {}
            }
        }
    }
}
