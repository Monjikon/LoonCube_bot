package ru.mclink.plugin.commands;

import org.bukkit.command.*;
import org.bukkit.entity.Player;
import ru.mclink.plugin.MCLinkPlugin;

/**
 * Команда /linkunlink — заглушка для Minecraft стороны.
 * Реальная отвязка происходит через бота командой unlink/отвязать.
 * Эта команда просто напоминает игроку как это сделать.
 */
public class LinkUnlinkCommand implements CommandExecutor {

    private final MCLinkPlugin plugin;

    public LinkUnlinkCommand(MCLinkPlugin plugin) {
        this.plugin = plugin;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!(sender instanceof Player)) {
            sender.sendMessage("§cТолько для игроков.");
            return true;
        }

        Player player = (Player) sender;

        // Проверяем текущую привязку
        plugin.getApiClient()
            .checkLink(player.getUniqueId().toString())
            .thenAccept(resp -> plugin.getServer().getScheduler().runTask(plugin, () -> {
                if (resp == null || !resp.has("linked") || !resp.get("linked").getAsBoolean()) {
                    player.sendMessage(plugin.msg("not_linked"));
                    return;
                }

                String platform = resp.has("platform") ? resp.get("platform").getAsString() : "?";
                player.sendMessage("§eЧтобы отвязать аккаунт, отправь команду §funlink §eв "
                        + platform.toUpperCase() + " боте.");
            }));

        return true;
    }
}
