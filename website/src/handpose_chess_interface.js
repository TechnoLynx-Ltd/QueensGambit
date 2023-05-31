import { init_hand_tracking } from "./handpose.js";
import { renderResult } from "./handpose.js"
import { camera } from "./handpose.js"

let xStepSize, yStepSize;
let hands;
let prev_is_click=false;
export async function init_hand_pose_interface() {
	await init_hand_tracking()

	xStepSize = camera.video.width / 8;
  	yStepSize = camera.video.height / 8;
  	
}

export async function detect_hand() {
	hands = await renderResult();
	if (hands.length > 0) {
    if(hands.length > 1) {
      alert("More than 1 hand is visible on the camera! Use only 1 hand to control the game!")
    }
		var table_coord = calc_table_coord(hands[0]);
        return {'is_hand_present': true, 'is_click': is_click(hands[0]), 'position': table_coord};
    }
    else {
    	return {'is_hand_present': false, 'is_click': false, 'position': null};	
    }
}

function is_click(hand) {
	// click if dip is lower than pip
	//var click = hand["keypoints"][6]['y'] <hand["keypoints"][7]['y'];

  // hand["keypoints"][7]['y'] - hand["keypoints"][6]['y'] > 0 then it's a click
  
  var index_dist = hand["keypoints"][7]['y'] - hand["keypoints"][6]['y']
  var middle_dist = hand["keypoints"][11]['y'] - hand["keypoints"][10]['y']
  var ring_dist = hand["keypoints"][15]['y'] - hand["keypoints"][14]['y']
  var pinky_dist = hand["keypoints"][19]['y'] - hand["keypoints"][18]['y']

  var dists = index_dist + middle_dist + ring_dist + pinky_dist
  var click = dists > 0;
	var result = !prev_is_click && click
	prev_is_click = click;
	return result;
	
}

function calc_table_coord(hand) {
	var x_coord = hand["keypoints"][0]['x'];
	var y_coord = hand["keypoints"][0]['y'];

	if(x_coord < 0) {
      x_coord = 0
    }
    if(y_coord < 0) {
      y_coord = 0
    }
    x_coord = camera.video.width - x_coord;
    x_coord = Math.floor(x_coord / xStepSize);
    y_coord = Math.floor(y_coord / yStepSize);

    if(x_coord > 7) 
    {
    	x_coord = 7;
    }
    if(y_coord > 7)
    {
    	y_coord = 7;
    }
    if(x_coord < 0) 
    {
    	x_coord = 0;
    }
    if(y_coord < 0)
    {
    	y_coord = 0;
    }
    return [x_coord, y_coord]
}