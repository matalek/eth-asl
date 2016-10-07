package pl.matal;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;
import java.util.Iterator;
import java.util.Set;

/**
 * Created by aleksander on 26.09.16.
 */
public class SetterWorker extends Worker<SetRequestQueue, SetRequest> {

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
                // Non-blocking version of handling responses that have arrived
                while (selector.selectNow() != 0) {
                    handleResponses();
                }

                // Non-blocking checking if there are new request in the queue
                SetRequest request = queue.getNoBlock();
                if (request != null) {
                    request.setTime(Request.DEQUEUE_TIME);
                    handleRequest(request);
                }
            } catch (IOException e) {
                e.printStackTrace();
            } // TODO: maybe add finally

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
        // TODO: add handling for delete
        StringBuilder serverRequest =  new StringBuilder("set ");
        serverRequest.append(request.getKey()).append(" ");
        for (int i = 0; i < 3; i++) {
            serverRequest.append(request.getParams()[i]).append(" ");
        }
        serverRequest.append("\r\n");
        serverRequest.append(request.getValue());
        serverRequest.append("\r\n");

        responseQueue.addRequest(request);

        request.setTime(Request.SEND_TO_SERVER_TIME);
        for (SocketChannel channel : serverChannels) {
            ByteBuffer buffer = ByteBuffer.wrap(serverRequest.toString().getBytes());
            channel.write(buffer); // TODO: should I add while loop here?
            buffer.clear();
        }
    }

    private void read(SelectionKey key) throws IOException {
        SocketChannel channel = (SocketChannel) key.channel();
        ByteBuffer buffer = ByteBuffer.allocate(IOManager.MESSAGE_SIZE);
        int numRead = channel.read(buffer);
        if (numRead == -1) {
            key.cancel();
        } else {
            String result = new String(buffer.array()).trim();
            buffer.clear();
            String[] resultLines = result.split("\r\n");
            int channelNumber = findChannelNumber(channel);

            for (int i = 0; i < resultLines.length; i++) {
                String line = resultLines[i];
                boolean success = line.trim().equals("STORED");
                responseQueue.registerResponse(channelNumber, success);
            }
        }
    }

    private int findChannelNumber(SocketChannel channel) {
        for (int i = 0; i < serverChannels.length; i++) {
            if (serverChannels[i].equals(channel)) {
                return i;
            }
        }
        return -1;
    }

}
