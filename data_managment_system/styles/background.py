import reflex as rx

def create_background():
    """
    Creates a NeonDB-inspired background with glowing, moving violet circles.
    """
    # Custom CSS for animations
    style_tag = rx.el.style(
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
            ("35vw", "rgba(139, 92, 246, 0.55)", "5%", "10%", "0s"),      # Violet 500
            ("45vw", "rgba(109, 40, 217, 0.45)", "35%", "55%", "-5s"),    # Violet 700
            ("30vw", "rgba(167, 139, 250, 0.40)", "60%", "15%", "-10s"),   # Violet 400
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
            inset="0",
            width="100%",
            height="100%",
            overflow="hidden",
            z_index="-1",
            pointer_events="none",
        ),
    )
0