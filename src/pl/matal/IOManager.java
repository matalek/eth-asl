package pl.matal;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.util.Iterator;
import java.util.Set;

/**
 * Created by aleksander on 26.09.16.
 */
public class IOManager {
    public static final int MESSAGE_SIZE = 4096;
    private static final int PROBE_FREQUENCY = 100;

    private MiddlewareServer server;
    private Selector selector;
    private int setsCounter = 0;
    private int getsCounter = 0;

    public IOManager(MiddlewareServer server) {
        this.server = server;
    }

    public void run() {
        try {
            runIO();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void runIO() throws IOException {
        // Selector for listening to all connections.
        selector = Selector.open();

        // On this socket we listen to new connections.
        ServerSocketChannel serverChannel = ServerSocketChannel.open();
        InetSocketAddress addr = new InetSocketAddress(server.getMyIp(), server.getMyPort());
        serverChannel.bind(addr);
        serverChannel.configureBlocking(false);
        serverChannel.register(selector, SelectionKey.OP_ACCEPT);

        while (true) {
            selector.select();
            Set<SelectionKey> keys = selector.selectedKeys();
            Iterator<SelectionKey> it = keys.iterator();

            while (it.hasNext()) {
                SelectionKey key = it.next();
                if (key.isAcceptable()) {
                    accept(key);
                } else if (key.isReadable()) {
                    read(key);
                }
                it.remove();
            }
        }
    }

    private void accept(SelectionKey key) throws IOException {
        ServerSocketChannel serverChannel = (ServerSocketChannel) key.channel();
        SocketChannel channel = serverChannel.accept();
        channel.configureBlocking(false);
        channel.register(selector, SelectionKey.OP_READ);
    }

    private void read(SelectionKey key) throws IOException {
        long currentTime = Request.getCurrentTime();
        SocketChannel channel = (SocketChannel) key.channel();
        ByteBuffer buffer = ByteBuffer.allocate(MESSAGE_SIZE);
        int numRead = channel.read(buffer);
        if (numRead == -1) {
            key.cancel();
        } else {
            String result = new String(buffer.array()).trim();
            buffer.clear();
            Request request = createRequest(channel, result);
            request.setTime(Request.RECEIVE_FROM_CLIENT_TIME, currentTime);
            server.handleRequest(request);
        }
    }

    private Request createRequest(SocketChannel channel, String input) {
        Request request;
        String[] parts = input.split("\\s+");
        if (!parts[0].equals("get")) {
            int[] params = new int[3];
            for (int i = 0; i < 3; i++) {
                params[i] = Integer.parseInt(parts[i + 2]);
            }
            getsCounter++;
            request = new SetRequest(channel, parts[1], params, parts[5], (getsCounter % PROBE_FREQUENCY) == 0);
        } else {
            setsCounter++;
            request = new GetRequest(channel, parts[1], (setsCounter % PROBE_FREQUENCY) == 0);
        }
        return request;
    }

}
