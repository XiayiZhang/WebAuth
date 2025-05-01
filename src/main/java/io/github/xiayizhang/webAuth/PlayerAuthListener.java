package io.github.xiayizhang.webAuth;

import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.UUID;

public class PlayerAuthListener implements Listener {
    private final WebAuth plugin;

    public PlayerAuthListener(WebAuth plugin){
        this.plugin = plugin;
    }
    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent event) {
        Player player = event.getPlayer();

        // 异步执行验证检查
        Bukkit.getScheduler().runTaskAsynchronously(plugin, () -> {
            boolean isVerified = checkPlayerVerification(player);
            if (!isVerified) {
                // 同步执行踢出操作
                Bukkit.getScheduler().runTask(plugin, () ->
                        player.kickPlayer("§c请先访问 §ehttp://127.0.0.1:5000/login §c注册并绑定账号！")
                );
            }
        });
    }

    private boolean checkPlayerVerification(Player player) {
        try {
            URL url = new URL("http://127.0.0.1:5000/check-player" + "?name=" + player.getName() + "&uuid=" + player.getUniqueId());
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setConnectTimeout(5000); // 5秒连接超时
            conn.setReadTimeout(5000);    // 5秒读取超时

            int responseCode = conn.getResponseCode();
            if (responseCode != 200) {
                plugin.getLogger().warning("验证API返回非200状态码: " + responseCode);
                return false;
            }

            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(conn.getInputStream()))) {
                String response = reader.readLine();
                return "VERIFIED".equals(response);
            }
        } catch (Exception e) {
            plugin.getLogger().severe("验证玩家时出错: " + e.getMessage());
            return false;
        }
    }
}
