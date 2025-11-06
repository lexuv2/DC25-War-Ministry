package com.backend.parser.controller;

import com.backend.shared.EndpointConstants;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;

@RestController
@RequestMapping(EndpointConstants.PARSER)
public class ParserController {

    String projectRoot = new File(System.getProperty("user.dir")).getParent();
    File parserDir = new File(projectRoot, "parser");
    // Ścieżka do Pythona w wirtualnym środowisku
    String pythonExecutable = new File(parserDir, "venv/Scripts/python").getAbsolutePath();
    // Skrypt główny
    String parserScript = new File(parserDir, "__main__.py").getAbsolutePath();


    @PostMapping("/pdf")
    public ResponseEntity<String> parsePdf(@RequestParam("file") MultipartFile file) throws IOException, InterruptedException {
        // Zapisz plik tymczasowo
        File inputFile = File.createTempFile("input-", ".pdf");
        file.transferTo(inputFile);

        File outputFile = File.createTempFile("output-", ".json");

        // Budowa komendy
        ProcessBuilder processBuilder = new ProcessBuilder(
                pythonExecutable,
                parserScript,
                //"--api-mock",
                "--input", inputFile.getAbsolutePath(),
                "--output", outputFile.getAbsolutePath()
        );

        // Katalog roboczy parsera (tam, gdzie jest setup.py itd.)
        processBuilder.directory(new File(parserDir.getAbsolutePath()));
        processBuilder.redirectErrorStream(true);

        // Uruchom proces
        Process process = processBuilder.start();

        // Czytaj ewentualny output Pythona (np. logi)
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            reader.lines().forEach(System.out::println);
        }

        int exitCode = process.waitFor();
        if (exitCode != 0) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Parser failed with exit code " + exitCode);
        }

        // Wczytaj wynik JSON
        String resultJson = Files.readString(outputFile.toPath());

        // Sprzątanie (opcjonalne)
        inputFile.delete();
        outputFile.delete();

        return ResponseEntity.ok(resultJson);
    }
}
