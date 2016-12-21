package pl.matal;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;
import java.util.Arrays;
import java.util.Iterator;
import java.util.Set;

/**
 * Created by aleksander on 26.09.16.
 *
 * Class representing thread forwarding set and delete requests.
 */
public class SetterWorker extends Worker<SetRequestQueue, SetRequest> {
    private static int activeRequests;
    private final static Object lock = new Object();

    private Selector selector;
    private SocketChannel[] serverChannels;
    private ResponseQueue responseQueue;

    public SetterWorker(SetRequestQueue queue) {
        super(queue);
    }

    @Override
    protected void runWorker() throws InterruptedException {
        while (true) {
            try {
                // Non-blocking version of handling responses that have arrived.
                if (selector.selectNow() != 0) {
                    handleResponses();
                }

                // Non-blocking checking if there are new request in the queue.
                SetRequest request = queue.getNoBlock();
                if (request != null) {
                    request.setTime(Request.DEQUEUE_TIME);
                    startActive();
                    handleRequest(request);
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private void handleResponses() throws IOException {
        Set<SelectionKey> keys = selector.selectedKeys();
        Iterator<SelectionKey> it = keys.iterator();

        while (it.hasNext()) {
            SelectionKey key = it.next();
            read(key);
            it.remove();
        }
    }

    @Override
    protected void connectToServers() throws IOException {
        selector = Selector.open();
        MemcachedServer[] servers = queue.getServers();
        serverChannels = new SocketChannel[servers.length];
        for (int i = 0; i < servers.length; i++) {
            serverChannels[i] = servers[i].connectAsync();
            serverChannels[i].register(selector, SelectionKey.OP_READ);
        }

        responseQueue = new ResponseQueue(serverChannels.length, this);
    }

    @Override
    protected void handleRequest(SetRequest request) throws IOException {
        // Creating a request to be sent to servers.
        StringBuilder serverRequest =  new StringBuilder("");
        if (request.isDelete()) {
            serverRequest.append("delete ");
        } else {
            serverRequest.append("set ");
        }
        serverRequest.append(request.getKey()).append(" ");

        if (!request.isDelete()) {
            for (int i = 0; i < 3; i++) {
                serverRequest.append(request.getParams()[i]).append(" ");
            }
            serverRequest.append("\r\n");
            serverRequest.append(request.getValue());
        }
        serverRequest.append("\r\n");

        responseQueue.addRequest(request);

        request.setTime(Request.SEND_TO_SERVER_TIME);
        for (SocketChannel channel : serverChannels) {
            buffer.put(serverRequest.toString().getBytes());
            buffer.flip();
            while (buffer.hasRemaining()){
                channel.write(buffer);
            }
            buffer.clear();
        }
    }

    private void read(SelectionKey key) throws IOException {
        SocketChannel channel = (SocketChannel) key.channel();
        int numRead = channel.read(buffer);
        if (numRead == -1) {
            key.cancel();
            buffer.clear();
        } else {
            String result = new String(Arrays.copyOf(buffer.array(), numRead)).trim();
            buffer.clear();
            int channelNumber = findChannelNumber(channel);
            // One network response can contain several request responses from
            // the server. Therefore, we need to iterate line by line.
            String[] resultLines = result.split("\r\n");
            for (String line : resultLines) {
                responseQueue.registerResponse(channelNumber, line.trim());
            }
        }
    }

    // Finds server number based on the channel on which we received
    // the response.
    private int findChannelNumber(SocketChannel channel) {
        for (int i = 0; i < serverChannels.length; i++) {
            if (serverChannels[i].equals(channel)) {
                return i;
            }
        }
        return -1;
    }

    private void startActive() {
        synchronized (lock) {
            activeRequests++;
        }
    }


    public void stopActive() {
        synchronized (lock) {
            activeRequests--;
        }
    }


    public static int getActiveRequests() {
        int res;
        synchronized (lock) {
            res = activeRequests;
        }
        return res;
    }
}
