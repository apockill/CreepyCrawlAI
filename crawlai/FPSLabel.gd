# MIT License
# Copyright (c) 2019 Lupo Dharkael

class_name FpsLabel

extends CanvasLayer


enum Position {TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT, NONE}

export (Position) var position = Position.TOP_LEFT
export(int) var margin : int = 5

var label : Label


func _ready() -> void:
	label = Label.new()
	add_child(label)
	get_tree().get_root().connect("size_changed", self, "update_position")
	update_position()

# pos should be of type Position
func set_position(pos : int):
	position = pos
	update_position()


func update_position():
	var viewport_size : Vector2 = get_viewport().size
	var label_size : Vector2 = label.rect_size
	
	match position:
		Position.TOP_LEFT:
			offset = Vector2(margin, margin)
		Position.BOTTOM_LEFT:
			offset = Vector2(margin, viewport_size.y - margin - label_size.y)
		Position.TOP_RIGHT:
			offset = Vector2(viewport_size.x - margin - label_size.x, margin)
		Position.BOTTOM_RIGHT:
			offset = Vector2(viewport_size.x - margin - label_size.x, viewport_size.y - margin - label_size.y)


func _process(_delta : float) -> void:
	label.text = "fps: " + str(Engine.get_frames_per_second())
