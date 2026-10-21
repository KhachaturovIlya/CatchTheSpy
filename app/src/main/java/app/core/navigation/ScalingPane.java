package app.core.navigation;

import javafx.scene.Parent;
import javafx.scene.layout.Region;
import javafx.scene.transform.Scale;

/**
 * Корень сцены, который масштабирует экран под размер окна.
 * Экраны свёрстаны в пикселях под базовое разрешение (DESIGN_WIDTH x DESIGN_HEIGHT);
 * контент раскладывается на «виртуальной» площади того же соотношения сторон,
 * что и окно, а затем сжимается/растягивается, чтобы точно его заполнить.
 */
public class ScalingPane extends Region {
    private static final double DESIGN_WIDTH = 1920;
    private static final double DESIGN_HEIGHT = 1080;

    private final Scale scale = new Scale(1, 1, 0, 0);
    private Parent content;

    public void setContent(Parent content) {
        if (this.content != null) this.content.getTransforms().remove(scale);
        this.content = content;
        content.getTransforms().add(scale);
        getChildren().setAll(content);
    }

    @Override
    protected void layoutChildren() {
        if (content == null) return;

        double width = getWidth();
        double height = getHeight();
        if (width <= 0 || height <= 0) return;

        double factor = Math.min(width / DESIGN_WIDTH, height / DESIGN_HEIGHT);
        scale.setX(factor);
        scale.setY(factor);
        content.resizeRelocate(0, 0, width / factor, height / factor);
    }
}
