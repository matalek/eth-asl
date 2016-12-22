package pl.matal;

import java.nio.channels.SocketChannel;

/**
 * Created by aleksander on 26.09.16.
 *
 * Class representing incoming requests.
 */
public abstract class Request {
    // Stored channel in order to send later response to the client.
    protected SocketChannel channel;
    protected String key;
    private boolean toLog;

    public static final int RECEIVE_FROM_CLIENT_TIME = 0;
    public static final int ENQUEUE_TIME = 1;
    public static final int DEQUEUE_TIME = 2;
    public static final int SEND_TO_SERVER_TIME = 3;
    public static final int RECEIVE_FROM_SERVER_TIME = 4;
    public static final int SEND_TO_CLIENT_TIME = 5;

    public static final int TYPE_SET = 0;
    public static final int TYPE_GET = 1;

    private long[] instrumentationTimes;
    private boolean successFlag = true;

    public Request(SocketChannel channel, String key, boolean toLog) {
        this.channel = channel;
        this.key = key;
        this.toLog = toLog;
        instrumentationTimes = new long[SEND_TO_CLIENT_TIME + 1];
    }

    public SocketChannel getChannel() {
        return channel;
    }

    public String getKey() {
        return key;
    }

    public boolean isToLog() {
        return toLog;
    }

    public void setSuccessFlag(boolean successFlag) {
        this.successFlag = successFlag;
    }

    public boolean getSuccessFlag() {
        return successFlag;
    }

    public abstract int getType();

    public String getLogString() {
        String type = (getType() == TYPE_GET ? "get" : "set");
        long tMw = instrumentationTimes[SEND_TO_CLIENT_TIME] - instrumentationTimes[RECEIVE_FROM_CLIENT_TIME];
        long tQueue = instrumentationTimes[DEQUEUE_TIME] - instrumentationTimes[ENQUEUE_TIME];
        long tServer = instrumentationTimes[RECEIVE_FROM_SERVER_TIME] - instrumentationTimes[SEND_TO_SERVER_TIME];
        long tHash = instrumentationTimes[ENQUEUE_TIME] - instrumentationTimes[RECEIVE_FROM_CLIENT_TIME];
        long tForw = instrumentationTimes[SEND_TO_SERVER_TIME] - instrumentationTimes[DEQUEUE_TIME];
        String res = type + " " + tMw + " " + tQueue + " " + tServer + " " + tHash + " " + tForw + " " + (successFlag ? 1 : 0);
//        int[] times = {RECEIVE_FROM_CLIENT_TIME, ENQUEUE_TIME, DEQUEUE_TIME, SEND_TO_SERVER_TIME,
//                RECEIVE_FROM_SERVER_TIME, SEND_TO_CLIENT_TIME};
//        for (int time : times) {
//            res += " " + instrumentationTimes[time];
//        }
        if (getType() == TYPE_GET) {
            res += " " + GetterWorker.getActiveWorkers();
        } else {
            res += " " + SetterWorker.getActiveRequests();
        }
        return res;
    }

    public void setTime(int timeNumber, long time) {
        instrumentationTimes[timeNumber] = time;
    }

    public void setTime(int timeNumber) {
        setTime(timeNumber, getCurrentTime());
    }

    public static long getCurrentTime() {
        return System.nanoTime() / 1000;
    }
}
