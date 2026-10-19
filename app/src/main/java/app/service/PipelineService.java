package app.service;

import app.domain.ParseRequest;
import app.domain.SourceType;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

public class PipelineService {
    private final ScriptRunner runner;
    private final Path outDir;

    public PipelineService(ScriptRunner runner, Path outDir) {
        this.runner = runner;
        this.outDir = outDir;
    }

    public void run(PipelineScript[] scripts, ParseRequest request, Consumer<String> log)
            throws Exception {
        Files.createDirectories(outDir);

        for (PipelineScript script : scripts) {
            List<Path> args = new ArrayList<>();

            for (SourceType type : script.sources()) {
                Path path = request.sources().get(type);
                if (path == null) {
                    throw new IllegalStateException(
                            "Source '" + type.title() + "' is required for " + script.name());
                }
                args.add(path);
            }
            for (String name : script.uses()) {
                Path used = outDir.resolve(name);
                if (!Files.exists(used)) {
                    throw new IllegalStateException(
                            script.name() + " needs " + name + ", but it does not exist yet");
                }
                args.add(used);
            }
            Path output = outDir.resolve(script.output());
            Files.deleteIfExists(output);
            args.add(output);

            log.accept("[" + script.name() + "] start");
            log.accept("[" + script.name() + "] args: " + args);

            int code = runner.run(script.resource(), args, log);
            if (code != 0) {
                throw new IllegalStateException(script.name() + " failed, exit code " + code);
            }
            if (!Files.exists(output)) {
                throw new IllegalStateException(
                        script.name() + " finished but did not create " + output.getFileName());
            }
            log.accept("[" + script.name() + "] done -> " + output
                    + " (" + Files.size(output) + " bytes)");
        }
    }
}