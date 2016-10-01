package pl.matal;

import com.sun.org.apache.bcel.internal.generic.Select;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.util.Iterator;
import java.util.Objects;
import java.util.Set;

/**
 * Created by aleksander on 26.09.16.
 */
public class IOManager implements Runnable {
    private static int MESSAGE_SIZE = 4096;

    private MiddlewareServer server;
    private Selector selector;

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
        InetSocketAddress addr = new InetSocketAddress("localhost", server.getPort());
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
        SocketChannel channel = (SocketChannel) key.channel();
        ByteBuffer buffer = ByteBuffer.allocate(MESSAGE_SIZE);
        int numRead = channel.read(buffer);
        if (numRead == -1) {
            key.cancel();
        } else {
            String result = new String(buffer.array()).trim();
            Request request = createRequest(channel, result);
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
            request = new SetRequest(channel, parts[1], params, parts[5]);
        } else {
            request = new GetRequest(channel, parts[1]);
        }
        return request;
    }

}
