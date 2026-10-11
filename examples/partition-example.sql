-- Design illustration only. Choose partitioning only after assessing foreign keys and uniqueness.
-- event_id uniqueness is per created_on here, NOT globally enforced across all days.
CREATE TABLE event_history (
    created_on DATE NOT NULL,
    event_id BINARY(16) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    payload JSON NOT NULL,
    PRIMARY KEY (created_on, event_id)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
PARTITION BY RANGE COLUMNS (created_on) (
    PARTITION p202610 VALUES LESS THAN ('2026-11-01'),
    PARTITION p202611 VALUES LESS THAN ('2026-12-01'),
    PARTITION p202612 VALUES LESS THAN ('2027-01-01'),
    PARTITION p_future VALUES LESS THAN (MAXVALUE)
);
-- p202610 also accepts earlier dates. Business validation must define the accepted date range.
-- Maintain future partitions in an approved DDL window and test metadata-lock impact.
