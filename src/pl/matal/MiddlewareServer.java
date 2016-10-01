package pl.matal;

/**
 * Created by aleksander on 26.09.16.
 */
public class MiddlewareServer {
    private static final int PORT = 11212;
    private static final int SERVER_COUNT = 5;

    private IOManager ioManager;
    private Hasher hasher;
    private SetRequestQueue setRequestQueue;
    private GetRequestQueue getRequestQueue;

    public MiddlewareServer() {
        ioManager = new IOManager(this);
        hasher = new Hasher();
        setRequestQueue = new SetRequestQueue(PORT + 1);
        getRequestQueue = new GetRequestQueue(PORT + 1);
    }

    public int getPort() {
        return PORT;
    }

    public SetRequestQueue getSetRequestQueue() {
        return setRequestQueue;
    }

    public GetRequestQueue getGetRequestQueue() {
        return getRequestQueue;
    }

    public void start() {
        new Thread(ioManager).start();
        setRequestQueue.startWorkers();
        getRequestQueue.startWorkers();
    }

    public void handleRequest(Request request) {
        hasher.setServerNumber(request, SERVER_COUNT);
        request.addToQueue(this);
    }
}
