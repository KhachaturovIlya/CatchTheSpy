package app.service;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

public class ScriptRunner {
    // Можно переопределить: -Dpython.path="C:\...\python.exe" или -Dpython.path=/usr/bin/python3
    private static final String PYTHON = System.getProperty("python.path", defaultPython());

    // На Windows интерпретатор называется python, на Linux/macOS — python3
    private static String defaultPython() {
        boolean windows = System.getProperty("os.name", "").toLowerCase().startsWith("windows");
        return windows ? "python" : "python3";
    }

    private Path scriptsDir;

    public int run(String scriptResource, List<Path> args, Consumer<String> onLine)
            throws IOException, InterruptedException {

        Path script = extract(scriptResource);

        List<String> command = new ArrayList<>();
        command.add(PYTHON);
        command.add("-u");
        command.add(script.toString());
        for (Path arg : args) {
            command.add(arg.toString());
        }

        ProcessBuilder pb = new ProcessBuilder(command);
        pb.redirectErrorStream(true);
        pb.environment().put("PYTHONIOENCODING", "utf-8");

        Process process = pb.start();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                onLine.accept(line);
            }
        }
        return process.waitFor();
    }

    private Path extract(String resource) throws IOException {
        if (scriptsDir == null) {
            scriptsDir = Files.createTempDirectory("catchthespy-scripts");
        }
        try (InputStream in = getClass().getResourceAsStream(resource)) {
            if (in == null) throw new IOException("Script not found: " + resource);
            Path target = scriptsDir.resolve(Path.of(resource).getFileName().toString());
            Files.copy(in, target, StandardCopyOption.REPLACE_EXISTING);
            return target;
        }
    }
}