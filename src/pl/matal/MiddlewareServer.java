package pl.matal;

import java.io.IOException;
import java.util.List;
import java.util.logging.FileHandler;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Created by aleksander on 26.09.16.
 */
public class MiddlewareServer {
    private static final String loggerName = "MiddlewareServerLogger";
    private static Logger logger;
    private final String myIp;
    private final int myPort;
    private final int serverCount;

    private IOManager ioManager;
    private Hasher hasher;
    private SetRequestQueue[] setRequestQueues;
    private GetRequestQueue[] getRequestQueues;

    public static Logger getLogger() {
        if (logger == null) {
            logger = Logger.getLogger(loggerName);
            logger.setLevel(Level.INFO);
            try {
                logger.addHandler(new FileHandler("middlewareData.log"));
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        return logger;
    }

    public MiddlewareServer(String myIp, int myPort, List<String> mcAddresses, int numThreadsPTP, int writeToCount) {
        this.myIp = myIp;
        this.myPort = myPort;
        ioManager = new IOManager(this);
        hasher = new Hasher();

        serverCount = mcAddresses.size();

        MemcachedServer[] servers = new MemcachedServer[serverCount];
        int counter = 0;
        for (String address : mcAddresses) {
            String[] parts = address.split(":");
            servers[counter] = new MemcachedServer(parts[0], Integer.parseInt(parts[1]));
            counter++;
        }

        setRequestQueues = new SetRequestQueue[serverCount];
        getRequestQueues = new GetRequestQueue[serverCount];
        for (int i = 0; i < serverCount; i++) {
            MemcachedServer[] setServers = new MemcachedServer[writeToCount];
            for (int j = 0; j < writeToCount; j++) {
                setServers[j] = servers[(i + j) % serverCount];
            }
            setRequestQueues[i] = new SetRequestQueue(setServers);
            getRequestQueues[i] = new GetRequestQueue(servers[i], numThreadsPTP);
        }
    }

    public int getMyPort() {
        return myPort;
    }

    public String getMyIp() {
        return myIp;
    }

    public void run() {
        for (int i = 0; i < serverCount; i++) {
            setRequestQueues[i].startWorkers();
            getRequestQueues[i].startWorkers();
        }
        ioManager.run();
    }

    public void handleRequest(Request request) {
        int serverNumber = hasher.getServerNumber(request, serverCount);
        request.setTime(Request.ENQUEUE_TIME);
        if (request.getType() == Request.TYPE_GET) {
            getRequestQueues[serverNumber].add((GetRequest) request);
        } else {
            setRequestQueues[serverNumber].add((SetRequest) request);
        }
    }
}
