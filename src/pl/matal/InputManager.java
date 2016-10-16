package pl.matal;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.util.Arrays;
import java.util.Iterator;
import java.util.Set;

/**
 * Created by aleksander on 26.09.16.
 */
public class InputManager {
    public static final int MESSAGE_SIZE = 1088;
    private static final int PROBE_FREQUENCY = 100;

    private MiddlewareServer server;
    private Selector selector;
    private int setsCounter = 0;
    private int getsCounter = 0;
    private ByteBuffer buffer;

    public InputManager(MiddlewareServer server) {
        this.server = server;
        buffer = ByteBuffer.allocate(MESSAGE_SIZE);
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
        int numRead = channel.read(buffer);
        if (numRead == -1) {
            // Client closed the connection.
            key.cancel();
            channel.close();
            buffer.clear();
        } else {
            String result = new String(Arrays.copyOf(buffer.array(), numRead)).trim();
            buffer.clear();
            Request request = createRequest(channel, result);
            request.setTime(Request.RECEIVE_FROM_CLIENT_TIME, currentTime);
            server.handleRequest(request);
        }
    }

    private Request createRequest(SocketChannel channel, String input) {
        Request request;
        String[] parts = input.split("\\s+");
        if (parts[0].equals("get")) {
            getsCounter++;
            boolean isToLog = false;
            if (getsCounter % PROBE_FREQUENCY == 0) {
                isToLog = true;
                getsCounter = 0;
            }
            request = new GetRequest(channel, parts[1], isToLog);
        } else {
            boolean isDelete = parts[0].equals("delete");
            int[] params = new int[3];
            if (!isDelete) {
                for (int i = 0; i < 3; i++) {
                    params[i] = Integer.parseInt(parts[i + 2]);
                }
            }
            setsCounter++;
            boolean isToLog = false;
            if (setsCounter % PROBE_FREQUENCY == 0) {
                isToLog = true;
                setsCounter = 0;
            }

            if (isDelete) {
                request = new SetRequest(channel, parts[1], params, "", isToLog, true);
            } else {
                request = new SetRequest(channel, parts[1], params, parts[5], isToLog, false);
            }
        }
        return request;
    }
}