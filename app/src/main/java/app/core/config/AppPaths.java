package app.core.config;

import java.nio.file.Path;

public final class AppPaths {
    private AppPaths() {}

    public static final Path HOME = Path.of(System.getProperty("user.home"), "CatchTheSpy");
    public static final Path OUT = HOME.resolve("out");
}