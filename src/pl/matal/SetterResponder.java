package pl.matal;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;
import java.util.Iterator;
import java.util.Set;

/**
 * Created by aleksander on 01.10.16.
 */
public class SetterResponder implements Runnable {
    private Selector selector;
    private SocketChannel[] serverChannels;
    private ResponseQueue responseQueue;

    public SetterResponder(SetterWorker worker, Selector selector, SocketChannel[] serverChannels) {
        this.selector = selector;
        this.serverChannels = serverChannels;
        responseQueue = new ResponseQueue(serverChannels.length, worker);
    }

    @Override
    public void run() {
        try {
            runResponder();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void runResponder() throws IOException {
        while (true) {
            selector.select();
            Set<SelectionKey> keys = selector.selectedKeys();
            Iterator<SelectionKey> it = keys.iterator();

            while (it.hasNext()) {
                SelectionKey key = it.next();
                read(key);
                it.remove();
            }
        }
    }

    public void addRequest(SetRequest request) {
        responseQueue.addRequest(request);
    }

    private void read(SelectionKey key) throws IOException {
        SocketChannel channel = (SocketChannel) key.channel();
        ByteBuffer buffer = ByteBuffer.allocate(IOManager.MESSAGE_SIZE);
        int numRead = channel.read(buffer);
        if (numRead == -1) {
            key.cancel();
        } else {
            String result = new String(buffer.array()).trim();
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
