from yolo_game_verify.cases.evidence import load_step_frames


def test_load_step_frames_orders_image_files(synthetic_frame_dir):
    frames = load_step_frames(synthetic_frame_dir)

    assert [frame.frame_index for frame in frames] == [0, 1, 2]
    assert frames[0].image_path.endswith("frame_000.png")
