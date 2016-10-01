package pl.matal;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.channels.SocketChannel;

/**
 * Created by aleksander on 01.10.16.
 */
public class MemcachedServer {
    private final String hostName;
    private final int port;

    public MemcachedServer(String hostName, int port) {
        this.hostName = hostName;
        this.port = port;
    }

    public Socket connectSync() throws IOException {
        Socket socket = new Socket(hostName, port);
        socket.setReuseAddress(true);
        return socket;
    }

    public SocketChannel connectAsync() throws IOException {
        SocketChannel channel = SocketChannel.open();
        channel.connect(new InetSocketAddress(hostName, port));
        channel.configureBlocking(false);
        return channel;
    }
}
