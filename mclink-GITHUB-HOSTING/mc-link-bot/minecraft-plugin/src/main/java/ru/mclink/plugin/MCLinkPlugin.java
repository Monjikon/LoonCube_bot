package ru.mclink.plugin;

import org.bukkit.plugin.java.JavaPlugin;
import ru.mclink.plugin.commands.LinkCommand;
import ru.mclink.plugin.commands.LinkStatusCommand;
import ru.mclink.plugin.commands.LinkUnlinkCommand;

public class MCLinkPlugin extends JavaPlugin {

    private static MCLinkPlugin instance;
    private ApiClient apiClient;

    @Override
    public void onEnable() {
        instance = this;
        saveDefaultConfig();

        String apiUrl    = getConfig().getString("api.url", "http://localhost:8080");
        String apiSecret = getConfig().getString("api.secret", "");
        int    timeout   = getConfig().getInt("api.timeout", 5);

        this.apiClient = new ApiClient(apiUrl, apiSecret, timeout);

        // Регистрируем команды
        getCommand("link").setExecutor(new LinkCommand(this));
        getCommand("linkstatus").setExecutor(new LinkStatusCommand(this));
        getCommand("linkunlink").setExecutor(new LinkUnlinkCommand(this));

        getLogger().info("MCLink включён! API: " + apiUrl);
    }

    @Override
    public void onDisable() {
        getLogger().info("MCLink выключен.");
    }

    public static MCLinkPlugin getInstance() { return instance; }
    public ApiClient getApiClient()          { return apiClient; }

    /** Форматирует строку из конфига: заменяет &X на цветовые коды. */
    public String msg(String key, Object... replacements) {
        String prefix = getConfig().getString("messages.prefix", "[MCLink] ")
                .replace("&", "§");
        String text   = getConfig().getString("messages." + key, key)
                .replace("&", "§");

        // Простая замена {placeholder} -> значение
        for (int i = 0; i + 1 < replacements.length; i += 2) {
            text = text.replace("{" + replacements[i] + "}", String.valueOf(replacements[i + 1]));
        }
        return prefix + text;
    }
}
