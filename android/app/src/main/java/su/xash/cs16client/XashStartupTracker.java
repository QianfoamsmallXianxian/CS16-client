package su.xash.cs16client;

public class XashStartupTracker {
    private static final XashStartupTracker INSTANCE = new XashStartupTracker();
    private volatile boolean xashStarted = false;
    private volatile long xashStartedAt = 0L;

    private XashStartupTracker() {
    }

    public static XashStartupTracker getInstance() {
        return INSTANCE;
    }

    public void markXashStarted() {
        this.xashStarted = true;
        this.xashStartedAt = System.currentTimeMillis();
    }

    public boolean isXashStarted() {
        return xashStarted;
    }

    public long getXashStartedAt() {
        return xashStartedAt;
    }

    public void reset() {
        xashStarted = false;
        xashStartedAt = 0L;
    }
}
