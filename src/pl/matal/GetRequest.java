package pl.matal;

import java.nio.channels.SocketChannel;

/**
 * Created by aleksander on 26.09.16.
 */
public class GetRequest extends Request {
    private String resultValue;

    public GetRequest(SocketChannel channel, String key) {
        super(channel, key);
    }

    @Override
    public void addToQueue(MiddlewareServer server) {
        server.getGetRequestQueue().add(this);
    }
}
