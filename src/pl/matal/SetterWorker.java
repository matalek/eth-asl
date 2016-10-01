package pl.matal;

import com.sun.xml.internal.bind.v2.runtime.reflect.Accessor;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Set;

import static java.lang.Thread.sleep;

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
    public void run() {
        try {
            connectToServers();
            runWorker();
        } catch (InterruptedException|IOException e) {
            e.printStackTrace();
        }
    }

    @Override
    protected void runWorker() throws InterruptedException {
        // TODO: change for something else than active waiting
        while (true) {
            try {
                while (selector.selectNow() != 0) {
                    handleResponses();
                }

                SetRequest request = queue.getNoBlock();
                if (request != null) {
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

    private void connectToServers() throws IOException {
        selector = Selector.open();
        MemcachedServer[] servers = queue.getServers();
        serverChannels = new SocketChannel[servers.length];
        for (int i = 0; i < servers.length; i++) {
            serverChannels[i] = servers[i].connectAsync();
            serverChannels[i].register(selector, SelectionKey.OP_READ);
        }

//        new Thread(new SetterResponder(this, selector, serverChannels)).start();
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
            // TODO: do something with result
            responseQueue.registerResponse(findChannelNumber(channel));
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
