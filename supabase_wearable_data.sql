CREATE TABLE IF NOT EXISTS wearable_data (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  client_email text NOT NULL,
  device_type text NOT NULL,
  resting_hr integer,
  hrv integer,
  sleep_score numeric,
  recovery_score numeric,
  synced_at timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone DEFAULT now()
);
