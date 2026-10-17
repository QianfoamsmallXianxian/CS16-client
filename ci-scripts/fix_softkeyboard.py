import pathlib, sys

p = pathlib.Path('android/app/src/main/java/su/xash/engine/util/SoftKeyboardPan.java')
if not p.exists():
    sys.exit(0)

p.write_text('''package su.xash.engine.util;
import android.app.Activity;
public class SoftKeyboardPan {
    public SoftKeyboardPan(Activity activity) {}
    public static void assistActivity(Activity activity) {}
}
''')
