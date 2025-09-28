# VLM Annotation Tool

An intuitive GUI tool for annotating images for Vision Language Model (VLM) training. This tool helps with fast and efficient labeling of images using predefined questions and answers.

## Features

- **Graphical user interface** with Tkinter for easy operation
- **Predefined questions** for consistent annotations
- **Keyboard shortcuts** for efficient workflow
- **Live preview** of generated answers
- **Flexible storage** with separate folders for labels and images
- **Delete mode** for automatic moving of processed files
- **JSON output** in the correct format for VLM training

## Installation

### Requirements

```bash
pip install opencv-python numpy tkinter pillow
```

### Project Structure

Create the following folders in your project directory:

```
project/
├── annotate/           # Input folder with images to be annotated
├── annotated_label/    # Output folder for JSON labels
├── annotated_images/   # Output folder for annotated images
└── data/
    └── deleted/        # Folder for processed/skipped images
```

## Usage

### Starting the Application

```bash
python vlm_annotation_tool.py
```

### Workflow

1. **Load image**: The first image is automatically loaded
2. **Select question**: Choose a predefined question or type a custom question
3. **Choose viewpoint**: Select the perspective of the image
4. **Add details**: Select relevant details about the image
5. **Check preview**: Review the generated answer
6. **Save**: Press 'Save' to save the annotation

### Keyboard Shortcuts

| Key | Function |
|-----|----------|
| `A` / `←` | Previous image |
| `D` / `→` | Next image |
| `S` | Save annotation |
| `O` | Skip current image |
| `1-4` | Select viewpoint |
| `Shift+1-8` | Toggle details |
| `Q` / `Esc` | Exit application |

## Configuration

Adjust the following variables in the script to match your project structure:

```python
input_folder = "annotate"                   # Input folder with images
output_folder_labels = "annotated_label"    # Output folder for JSON files
output_folder_images = "annotated_images"   # Output folder for images
delete_folder = "data/deleted"              # Folder for processed files
enable_delete_mode = False                  # Delete mode at startup
```

### Customizing Predefined Content

#### Modifying Questions

```python
PREDEFINED_QUESTIONS = [
    "What do you see in this image?",
    "Describe the position of the cow.",
    "What is the posture of the animal?"
]
```

#### Modifying Viewpoints

```python
PREDEFINED_VIEWPOINTS = {
    "1": "I see the side view",
    "2": "I see the front view", 
    "3": "I see the rear view",
    "4": "I see an oblique perspective"
}
```

#### Modifying Details

```python
PREDEFINED_DETAILS = {
    "1": "through this we see the front legs",
    "2": "the cow's head is lying",
    "3": "the hind legs are visible",
    "4": "the tail is visible",
    "5": "the body is fully visible",
    "6": "only the head is visible",
    "7": "the cow is standing upright",
    "8": "the cow is lying on the ground"
}
```

## Output Format

The tool generates JSON files in the following format:

```json
{
  "id": "image_001",
  "image": "annotated_images/image_001.jpg",
  "conversations": [
    {
      "from": "human",
      "value": "<image>\nWhat do you see in this image?"
    },
    {
      "from": "gpt",
      "value": "I see the side view, through this we see the front legs, the cow is standing upright."
    }
  ]
}
```

## Delete Mode

When **Delete Mode** is enabled:
- Saved images are automatically moved to the `delete_folder`
- Skipped images are also moved
- This prevents the same image from being annotated twice

## Supported File Formats

- **Input images**: `.png`, `.jpg`, `.jpeg`
- **Output labels**: `.json` (UTF-8 encoded)

## Troubleshooting

### Common Issues

**Error: "No images found!"**
- Check if the `input_folder` exists and contains images
- Verify that file extensions are correct (png, jpg, jpeg)

**Error when saving**
- Check write permissions for the output folders
- Ensure output folders exist or are automatically created

**Image not displaying**
- Check if OpenCV and PIL are correctly installed
- Verify that the image format is supported

### Performance Tips

- Use smaller image sizes for faster loading
- Enable delete mode to avoid processing the same images multiple times
- Use keyboard shortcuts for faster annotation workflow

## Use Cases

This tool is particularly useful for:
- **Agricultural AI**: Annotating livestock images for behavior analysis
- **Computer Vision Research**: Creating training datasets for object detection
- **Educational Projects**: Teaching annotation techniques
- **Custom VLM Training**: Preparing data for domain-specific language models

## Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comments for complex functions
- Test with different image formats and sizes
- Update documentation for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- Initial release
- Basic annotation functionality
- Predefined questions and answers
- Delete mode functionality
- Keyboard shortcuts for efficient workflow

### Future Roadmap

- [ ] Batch processing capabilities
- [ ] Export to different annotation formats (COCO, YOLO)
- [ ] Integration with cloud storage
- [ ] Multi-language support
- [ ] Annotation quality validation
- [ ] Team collaboration features

## Acknowledgments

- Built with Python and Tkinter for cross-platform compatibility
- Uses OpenCV for image processing
- Designed for efficiency in VLM training data preparation

## Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with detailed information about your problem

For feature requests, please open an issue with the "enhancement" label.
