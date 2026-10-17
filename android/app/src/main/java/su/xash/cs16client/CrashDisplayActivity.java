package su.xash.cs16client;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;
import android.widget.ScrollView;
import android.graphics.Color;

public class CrashDisplayActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        String err = getIntent().getStringExtra("error_msg");
        if (err == null) err = "Unknown error";
        
        ScrollView scroll = new ScrollView(this);
        TextView tv = new TextView(this);
        tv.setText(err);
        tv.setTextColor(Color.RED);
        tv.setTextSize(12);
        tv.setPadding(20, 20, 20, 20);
        tv.setTextIsSelectable(true);
        scroll.addView(tv);
        setContentView(scroll);
    }
}
