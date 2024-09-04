STATES_TABLE_PATH = "states"
TRACKER_INFO_TABLE_PATH = "tracker_info"


get_tracker_info = f"""
    SELECT
        chat_id,
        email,
        password,
        last_reference_id,
        last_edited,
        last_error_timestamp,
        last_updated_timestamp,
    FROM `{TRACKER_INFO_TABLE_PATH}`
    WHERE NOT is_deleted;
"""

update_tracker_info = f"""
    DECLARE $chat_ids AS List<Int64>;
    DECLARE $emails AS List<Utf8>;
    DECLARE $last_reference_ids AS List<Utf8?>;
    DECLARE $last_editeds AS List<Utf8?>;
    DECLARE $last_error_timestamps AS List<Uint64?>;
    DECLARE $last_updated_timestamps AS List<Uint64?>;

    $updated_rows = (
        SELECT
            entry.0 AS chat_id,
            entry.1 AS email,
            entry.2 AS last_reference_id,
            entry.3 AS last_edited,
            entry.4 AS last_error_timestamp,
            entry.5 AS last_updated_timestamp,
        FROM (
            SELECT
                ListZip(
                    $chat_ids,
                    $emails,
                    $last_reference_ids,
                    $last_editeds,
                    $last_error_timestamps,
                    $last_updated_timestamps,
                ) AS entries
        )
        FLATTEN LIST BY entries AS entry
    );

    UPSERT INTO `{TRACKER_INFO_TABLE_PATH}`
    SELECT * FROM $updated_rows;
"""

add_tracking = f"""
    DECLARE $chat_id AS Int64;
    DECLARE $email AS Utf8;
    DECLARE $password AS String;
    DECLARE $last_updated_timestamp AS Uint64;
    
    UPSERT INTO `{TRACKER_INFO_TABLE_PATH}`
        (chat_id, email, password, last_reference_id, last_edited, last_error_timestamp, last_updated_timestamp, is_deleted)
    VALUES ($chat_id, $email, $password, NULL, NULL, NULL, $last_updated_timestamp, False);
"""

get_chat_trackings = f"""
    DECLARE $chat_id AS Int64;
    
    SELECT email
    FROM `{TRACKER_INFO_TABLE_PATH}`
    WHERE
        chat_id = $chat_id
        AND NOT is_deleted;
"""

delete_tracking = f"""
    DECLARE $chat_id AS Int64;
    DECLARE $email AS Utf8;

    UPSERT INTO `{TRACKER_INFO_TABLE_PATH}`
        (chat_id, email, is_deleted)
    VALUES ($chat_id, $email, True)
"""

get_user_state = f"""
    DECLARE $chat_id AS Int64;

    SELECT state
    FROM `{STATES_TABLE_PATH}`
    WHERE chat_id == $chat_id;
"""

set_user_state = f"""
    DECLARE $chat_id AS Int64;
    DECLARE $state AS Utf8?;

    UPSERT INTO `{STATES_TABLE_PATH}` (`chat_id`, `state`)
    VALUES ($chat_id, $state);
"""
