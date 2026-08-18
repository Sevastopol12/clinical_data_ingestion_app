import reflex as rx

def create_background():
    """
    Creates a NeonDB-inspired background with glowing, moving violet circles.
    """
    # Custom CSS for animations
    # We use rx.el.style to inject keyframes directly into the page
    style_tag = rx.el.Style(
        """
        @keyframes float {
            0% { transform: translate(0, 0); }
            33% { transform: translate(30px, -50px); }
            66% { transform: translate(-20px, 20px); }
            100% { transform: translate(0, 0); }
        }
        @keyframes pulse {
            0%, 100% { opacity: 0.4; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
        }
        .glow-blob {
            position: absolute;
            border-radius: 50%;
            filter: blur(80px);
            z-index: -1;
            pointer-events: none;
            mix-blend-mode: screen;
            animation: float 20s infinite ease-in-out, pulse 10s infinite ease-in-out;
        }
        """
    )

    # Blob configurations: (size, color, top, left, animation_delay)
    blobs = [
        ("400px", "rgba(139, 92, 246, 0.6)", "10%", "10%", "0s"),      # Violet 500
        ("600px", "rgba(109, 40, 217, 0.4)", "40%", "60%", "-5s"),    # Violet 700
        ("500px", "rgba(167, 139, 250, 0.5)", "70%", "20%", "-10s"),   # Violet 400
    ]

    blob_elements = []
    for size, color, top, left, delay in blobs:
        blob_elements.append(
            rx.box(
                width=size,
                height=size,
                bg=color,
                top=top,
                left=left,
                class_name="glow-blob",
                style={
                    "animation_delay": delay,
                },
            )
        )

    return rx.fragment(
        style_tag,
        rx.box(
            *blob_elements,
            position="fixed",
            top="0",
            left="0",
            width="100vw",
            height="100vh",
            overflow="hidden",
            z_index="-1",
            pointer_events="none",
        ),
    )
0