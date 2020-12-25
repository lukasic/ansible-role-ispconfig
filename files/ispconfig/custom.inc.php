<?php

class remoting_custom extends remoting {

	public function sites_database_user_get_id_by_name($session_id, $username)
	{
		global $app;

		$app->uses('remoting_lib');

		# todo: fix sql injection
		$sql = "select database_user_id from web_database_user where database_user = '$username'";
		$records = $app->db->queryAllRecords($sql);

		foreach($records as $rec) {
			return $rec['database_user_id'];
		}

		return null;
	}

	public function sites_database_get_id_by_name($session_id, $database_name)
	{
		global $app;

		$app->uses('remoting_lib');

		# todo: fix sql injection
		$sql = "select database_id from web_database where database_name = '$database_name'";
		$records = $app->db->queryAllRecords($sql);

		foreach($records as $rec) {
			return $rec['database_id'];
		}

		return null;
	}

	public function sites_domain_get_id_by_name($session_id, $domain)
	{
		global $app;

		$app->uses('remoting_lib');

		# todo: fix sql injection
		$sql = "select domain_id from web_domain where domain = '$domain'";
		$records = $app->db->queryAllRecords($sql);

		foreach($records as $rec) {
			return $rec['domain_id'];
		}

		return null;
	}

}
