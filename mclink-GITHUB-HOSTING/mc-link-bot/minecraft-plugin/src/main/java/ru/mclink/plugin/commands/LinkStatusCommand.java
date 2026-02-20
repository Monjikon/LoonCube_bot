package ru.mclink.plugin.commands;

import com.google.gson.JsonObject;
import org.bukkit.command.*;
import org.bukkit.entity.Player;
import ru.mclink.plugin.MCLinkPlugin;

public class LinkStatusCommand implements CommandExecutor {

    private final MCLinkPlugin plugin;

    public LinkStatusCommand(MCLinkPlugin plugin) {
        this.plugin = plugin;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!(sender instanceof Player)) {
            sender.sendMessage("§cТолько для игроков.");
            return true;
        }

        Player player = (Player) sender;

        plugin.getApiClient()
            .checkLink(player.getUniqueId().toString())
            .thenAccept(resp -> plugin.getServer().getScheduler().runTask(plugin, () -> {
                if (resp != null && resp.has("linked") && resp.get("linked").getAsBoolean()) {
                    String platform = resp.has("platform") ? resp.get("platform").getAsString() : "?";
                    String date     = resp.has("linked_at")
                            ? resp.get("linked_at").getAsString().substring(0, 10)
                            : "?";
                    player.sendMessage(plugin.msg("link_status", "platform", platform, "date", date));
                } else {
                    player.sendMessage(plugin.msg("not_linked"));
                    player.sendMessage("§7Введи §f/link §7чтобы привязать аккаунт.");
                }
            }));

        return true;
    }
}
