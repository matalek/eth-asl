package pl.matal;

import java.nio.channels.SocketChannel;

/**
 * Created by aleksander on 26.09.16.
 */
public abstract class Request {
    protected SocketChannel channel;
    protected String key;
    protected int serverNumber;

    public Request(SocketChannel channel, String key) {
        this.channel = channel;
        this.key = key;
    }

    public SocketChannel getChannel() {
        return channel;
    }

    public String getKey() {
        return key;
    }

    public int getServerNumber() {
        return serverNumber;
    }

    public void setServerNumber(int serverNumber) {
        this.serverNumber = serverNumber;
    }

    public abstract void addToQueue(MiddlewareServer server);

    @Override
    public String toString() {
        return "Request{" +
                "key='" + key + '\'' +
                ", serverNumber=" + serverNumber +
                '}';
    }
}
